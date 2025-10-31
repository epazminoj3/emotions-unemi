from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import json

User = get_user_model()


class EmotionAnalysis(models.Model):
    """
    Modelo para almacenar los análisis de emociones realizados.
    """
    
    # Información básica
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='emotion_analyses',
        verbose_name='Usuario'
    )
    
    # Imagen analizada
    image = models.ImageField(
        upload_to='emotion_analysis/%Y/%m/%d/', 
        verbose_name='Imagen Analizada'
    )
    
    # Resultados del análisis
    faces_detected = models.PositiveIntegerField(
        default=0,
        verbose_name='Rostros Detectados'
    )
    
    analysis_results = models.JSONField(
        default=dict,
        verbose_name='Resultados del Análisis',
        help_text='Resultados completos del análisis en formato JSON'
    )
    
    # Emoción dominante general (si hay múltiples rostros, la más frecuente)
    dominant_emotion = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Emoción Dominante'
    )
    
    # Confianza promedio
    average_confidence = models.FloatField(
        default=0.0,
        verbose_name='Confianza Promedio'
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Actualización'
    )
    
    # Metadatos adicionales
    processing_time = models.FloatField(
        default=0.0,
        verbose_name='Tiempo de Procesamiento (segundos)'
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name='Notas',
        help_text='Notas adicionales sobre el análisis'
    )
    
    class Meta:
        verbose_name = 'Análisis de Emoción'
        verbose_name_plural = 'Análisis de Emociones'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['dominant_emotion']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Análisis de {self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    def get_emotion_translation(self, emotion):
        """
        Traduce las emociones del inglés al español.
        """
        translations = {
            'neutral': 'Neutral',
            'happiness': 'Felicidad',
            'surprise': 'Sorpresa',
            'sadness': 'Tristeza',
            'anger': 'Ira',
            'disgust': 'Disgusto',
            'fear': 'Miedo',
            'contempt': 'Desprecio'
        }
        return translations.get(emotion, emotion.title())
    
    def get_dominant_emotion_display(self):
        """
        Retorna la emoción dominante traducida al español.
        """
        if self.dominant_emotion:
            return self.get_emotion_translation(self.dominant_emotion)
        return 'Sin determinar'
    
    def get_faces_summary(self):
        """
        Retorna un resumen detallado de las emociones detectadas en todos los rostros.
        """
        if not self.analysis_results or 'faces_analysis' not in self.analysis_results:
            return []
        
        # Colores para cada emoción
        emotion_colors = {
            'neutral': '#6B7280',
            'happiness': '#10B981',
            'surprise': '#F59E0B',
            'sadness': '#3B82F6',
            'anger': '#EF4444',
            'disgust': '#84CC16',
            'fear': '#8B5CF6',
            'contempt': '#F97316'
        }
        
        summary = []
        for idx, face in enumerate(self.analysis_results['faces_analysis']):
            dominant_emotion = face.get('dominant_emotion', '')
            confidence = face.get('confidence', 0)
            
            # Convertir confianza a porcentaje si está en decimal
            if confidence < 1:
                confidence = confidence * 100
            
            # Obtener todas las emociones del rostro
            emotions_detail = {}
            emotions_data = face.get('emotions', {}) or face.get('all_emotions', {})
            
            for emotion_en, value in emotions_data.items():
                emotion_es = self.get_emotion_translation(emotion_en)
                # Convertir a porcentaje si está en decimal
                percentage = value * 100 if value < 1 else value
                emotions_detail[emotion_en] = {
                    'name': emotion_es,
                    'percentage': round(percentage, 1),
                    'color': emotion_colors.get(emotion_en, '#6B7280')
                }
            
            face_summary = {
                'face_id': idx + 1,
                'dominant_emotion': dominant_emotion,
                'dominant_emotion_name': self.get_emotion_translation(dominant_emotion),
                'dominant_emotion_color': emotion_colors.get(dominant_emotion, '#6B7280'),
                'dominant_emotion_confidence': round(emotions_data.get(dominant_emotion, 0) * 100 if emotions_data.get(dominant_emotion, 0) < 1 else emotions_data.get(dominant_emotion, 0), 1),
                'confidence': round(confidence, 1),
                'emotions': emotions_detail,
                'face_image': face.get('face_image')  # Agregar imagen del rostro si existe
            }
            summary.append(face_summary)
        
        return summary
    
    def get_emotion_distribution(self):
        """
        Retorna la distribución de emociones en todos los rostros detectados.
        Formato: {emotion_en: percentage} para usar en gráficos
        """
        if not self.analysis_results or 'faces_analysis' not in self.analysis_results:
            return {}
        
        emotion_count = {}
        total_faces = len(self.analysis_results['faces_analysis'])
        
        if total_faces == 0:
            return {}
        
        for face in self.analysis_results['faces_analysis']:
            emotion = face.get('dominant_emotion', 'unknown')
            if emotion != 'unknown':
                emotion_count[emotion] = emotion_count.get(emotion, 0) + 1
        
        # Convertir a porcentajes para el gráfico
        emotion_percentages = {}
        for emotion, count in emotion_count.items():
            percentage = round((count / total_faces) * 100, 1)
            if percentage > 0:
                emotion_percentages[emotion] = percentage
        
        return emotion_percentages
    
    def save(self, *args, **kwargs):
        """
        Override del método save para calcular emoción dominante y confianza promedio.
        """
        if self.analysis_results and 'faces_analysis' in self.analysis_results:
            faces_analysis = self.analysis_results['faces_analysis']
            
            if faces_analysis:
                # Calcular emoción dominante (más frecuente)
                emotions = [face.get('dominant_emotion') for face in faces_analysis if face.get('dominant_emotion')]
                if emotions:
                    # Contar frecuencia de emociones
                    emotion_count = {}
                    for emotion in emotions:
                        emotion_count[emotion] = emotion_count.get(emotion, 0) + 1
                    
                    # Obtener la más frecuente
                    self.dominant_emotion = max(emotion_count, key=emotion_count.get)
                
                # Calcular confianza promedio
                confidences = [face.get('confidence', 0) for face in faces_analysis]
                if confidences:
                    self.average_confidence = sum(confidences) / len(confidences)
        
        super().save(*args, **kwargs)


class EmotionStatistics(models.Model):
    """
    Modelo para almacenar estadísticas agregadas de emociones por usuario.
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='emotion_statistics',
        verbose_name='Usuario'
    )
    
    # Contadores de emociones
    total_analyses = models.PositiveIntegerField(
        default=0,
        verbose_name='Total de Análisis'
    )
    
    total_faces_detected = models.PositiveIntegerField(
        default=0,
        verbose_name='Total de Rostros Detectados'
    )
    
    # Distribución de emociones
    neutral_count = models.PositiveIntegerField(default=0)
    happiness_count = models.PositiveIntegerField(default=0)
    surprise_count = models.PositiveIntegerField(default=0)
    sadness_count = models.PositiveIntegerField(default=0)
    anger_count = models.PositiveIntegerField(default=0)
    disgust_count = models.PositiveIntegerField(default=0)
    fear_count = models.PositiveIntegerField(default=0)
    contempt_count = models.PositiveIntegerField(default=0)
    
    # Emoción más frecuente
    most_frequent_emotion = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Emoción Más Frecuente'
    )
    
    # Promedios
    average_confidence = models.FloatField(
        default=0.0,
        verbose_name='Confianza Promedio'
    )
    
    average_faces_per_analysis = models.FloatField(
        default=0.0,
        verbose_name='Rostros Promedio por Análisis'
    )
    
    # Timestamps
    last_updated = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Actualización'
    )
    
    class Meta:
        verbose_name = 'Estadística de Emociones'
        verbose_name_plural = 'Estadísticas de Emociones'
    
    def __str__(self):
        return f"Estadísticas de {self.user.username}"
    
    def update_statistics(self):
        """
        Actualiza las estadísticas basadas en los análisis del usuario.
        """
        analyses = EmotionAnalysis.objects.filter(user=self.user)
        
        # Resetear contadores
        self.total_analyses = analyses.count()
        self.total_faces_detected = 0
        
        emotion_counts = {
            'neutral': 0,
            'happiness': 0,
            'surprise': 0,
            'sadness': 0,
            'anger': 0,
            'disgust': 0,
            'fear': 0,
            'contempt': 0
        }
        
        total_confidence = 0
        confidence_count = 0
        
        for analysis in analyses:
            self.total_faces_detected += analysis.faces_detected
            
            # Intentar diferentes estructuras de datos
            if analysis.analysis_results:
                faces_data = None
                
                # Intentar con 'faces_analysis'
                if 'faces_analysis' in analysis.analysis_results:
                    faces_data = analysis.analysis_results['faces_analysis']
                # Intentar con 'faces'
                elif 'faces' in analysis.analysis_results:
                    faces_data = analysis.analysis_results['faces']
                # Si no hay estructura, usar dominant_emotion del analysis
                elif analysis.dominant_emotion:
                    if analysis.dominant_emotion in emotion_counts:
                        emotion_counts[analysis.dominant_emotion] += analysis.faces_detected
                    if analysis.average_confidence > 0:
                        total_confidence += analysis.average_confidence * analysis.faces_detected
                        confidence_count += analysis.faces_detected
                    continue
                
                if faces_data:
                    for face in faces_data:
                        # Buscar emoción dominante en diferentes claves posibles
                        emotion = face.get('dominant_emotion') or face.get('emotion')
                        if emotion in emotion_counts:
                            emotion_counts[emotion] += 1
                        
                        confidence = face.get('confidence', 0) * 100 if face.get('confidence', 0) < 1 else face.get('confidence', 0)
                        total_confidence += confidence
                        confidence_count += 1
        
        # Actualizar contadores individuales
        self.neutral_count = emotion_counts['neutral']
        self.happiness_count = emotion_counts['happiness']
        self.surprise_count = emotion_counts['surprise']
        self.sadness_count = emotion_counts['sadness']
        self.anger_count = emotion_counts['anger']
        self.disgust_count = emotion_counts['disgust']
        self.fear_count = emotion_counts['fear']
        self.contempt_count = emotion_counts['contempt']
        
        # Calcular emoción más frecuente
        if emotion_counts:
            self.most_frequent_emotion = max(emotion_counts, key=emotion_counts.get)
        
        # Calcular promedios
        if confidence_count > 0:
            self.average_confidence = total_confidence / confidence_count
        
        if self.total_analyses > 0:
            self.average_faces_per_analysis = self.total_faces_detected / self.total_analyses
        
        self.save()
    
    def get_emotion_distribution_dict(self):
        """
        Retorna un diccionario con la distribución de emociones.
        """
        total = (self.neutral_count + self.happiness_count + self.surprise_count + 
                self.sadness_count + self.anger_count + self.disgust_count + 
                self.fear_count + self.contempt_count)
        
        if total == 0:
            return {}
        
        return {
            'Neutral': round((self.neutral_count / total) * 100, 2),
            'Felicidad': round((self.happiness_count / total) * 100, 2),
            'Sorpresa': round((self.surprise_count / total) * 100, 2),
            'Tristeza': round((self.sadness_count / total) * 100, 2),
            'Ira': round((self.anger_count / total) * 100, 2),
            'Disgusto': round((self.disgust_count / total) * 100, 2),
            'Miedo': round((self.fear_count / total) * 100, 2),
            'Desprecio': round((self.contempt_count / total) * 100, 2),
        }
