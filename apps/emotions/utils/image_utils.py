"""
Utilidades para la aplicación de detección de emociones.
"""
import os
import cv2
import numpy as np
from PIL import Image
import base64
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings


def validate_image_file(image_file):
    """
    Valida que un archivo sea una imagen válida.
    
    Args:
        image_file: Archivo de imagen a validar
        
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        # Verificar que sea una imagen válida
        img = Image.open(image_file)
        img.verify()
        
        # Verificar formato
        if img.format not in ['JPEG', 'PNG', 'GIF', 'BMP']:
            return False, f"Formato no soportado: {img.format}"
        
        # Verificar dimensiones mínimas
        if img.width < 64 or img.height < 64:
            return False, "La imagen debe tener al menos 64x64 píxeles"
        
        # Verificar dimensiones máximas
        if img.width > 4096 or img.height > 4096:
            return False, "La imagen es demasiado grande (máximo 4096x4096)"
        
        return True, None
        
    except Exception as e:
        return False, f"Error al validar imagen: {str(e)}"


def resize_image_for_web(image_path, max_width=800, max_height=600, quality=85):
    """
    Redimensiona una imagen para visualización web manteniendo la proporción.
    
    Args:
        image_path: Ruta de la imagen original
        max_width: Ancho máximo
        max_height: Alto máximo
        quality: Calidad JPEG (1-100)
        
    Returns:
        str: Ruta de la imagen redimensionada
    """
    try:
        with Image.open(image_path) as img:
            # Calcular nuevas dimensiones manteniendo proporción
            ratio = min(max_width / img.width, max_height / img.height)
            
            if ratio < 1:
                new_width = int(img.width * ratio)
                new_height = int(img.height * ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Guardar imagen redimensionada
            base_name, ext = os.path.splitext(image_path)
            web_path = f"{base_name}_web{ext}"
            
            if img.format == 'JPEG':
                img.save(web_path, 'JPEG', quality=quality, optimize=True)
            else:
                img.save(web_path, img.format, optimize=True)
            
            return web_path
            
    except Exception as e:
        print(f"Error al redimensionar imagen: {str(e)}")
        return image_path  # Retornar original si hay error


def convert_base64_to_image(base64_string, save_path=None):
    """
    Convierte una cadena base64 a una imagen.
    
    Args:
        base64_string: Cadena base64 de la imagen
        save_path: Ruta donde guardar la imagen (opcional)
        
    Returns:
        PIL.Image: Objeto imagen de PIL
    """
    try:
        # Remover el header si existe
        if ',' in base64_string:
            header, data = base64_string.split(',', 1)
        else:
            data = base64_string
        
        # Decodificar base64
        image_data = base64.b64decode(data)
        
        # Crear imagen desde bytes
        image = Image.open(BytesIO(image_data))
        
        # Guardar si se especifica ruta
        if save_path:
            image.save(save_path)
        
        return image
        
    except Exception as e:
        raise ValueError(f"Error al convertir base64 a imagen: {str(e)}")


def image_to_base64(image_path):
    """
    Convierte una imagen a cadena base64.
    
    Args:
        image_path: Ruta de la imagen
        
    Returns:
        str: Cadena base64 de la imagen
    """
    try:
        with open(image_path, 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Detectar tipo MIME
            _, ext = os.path.splitext(image_path)
            mime_type = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.bmp': 'image/bmp'
            }.get(ext.lower(), 'image/jpeg')
            
            return f"data:{mime_type};base64,{encoded_string}"
            
    except Exception as e:
        raise ValueError(f"Error al convertir imagen a base64: {str(e)}")


def draw_emotion_results(image_path, analysis_results, output_path=None):
    """
    Dibuja los resultados del análisis de emociones sobre la imagen.
    
    Args:
        image_path: Ruta de la imagen original
        analysis_results: Resultados del análisis de emociones
        output_path: Ruta donde guardar la imagen con anotaciones
        
    Returns:
        str: Ruta de la imagen con anotaciones
    """
    try:
        # Cargar imagen
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"No se pudo cargar la imagen: {image_path}")
        
        # Obtener análisis de rostros
        faces_analysis = analysis_results.get('faces_analysis', [])
        
        # Configuración de colores para emociones
        emotion_colors = {
            'neutral': (128, 128, 128),     # Gris
            'happiness': (0, 255, 0),       # Verde
            'surprise': (0, 255, 255),      # Amarillo
            'sadness': (255, 0, 0),         # Azul
            'anger': (0, 0, 255),           # Rojo
            'disgust': (0, 128, 0),         # Verde oscuro
            'fear': (128, 0, 128),          # Púrpura
            'contempt': (255, 165, 0)       # Naranja
        }
        
        # Dibujar cada rostro detectado
        for face in faces_analysis:
            coords = face.get('coordinates', {})
            x = coords.get('x', 0)
            y = coords.get('y', 0)
            w = coords.get('width', 0)
            h = coords.get('height', 0)
            
            emotion = face.get('dominant_emotion', 'neutral')
            confidence = face.get('confidence', 0)
            
            # Color para esta emoción
            color = emotion_colors.get(emotion, (255, 255, 255))
            
            # Dibujar rectángulo alrededor del rostro
            cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
            
            # Traducir emoción
            emotion_translations = {
                'neutral': 'Neutral',
                'happiness': 'Felicidad',
                'surprise': 'Sorpresa',
                'sadness': 'Tristeza',
                'anger': 'Ira',
                'disgust': 'Disgusto',
                'fear': 'Miedo',
                'contempt': 'Desprecio'
            }
            
            emotion_text = emotion_translations.get(emotion, emotion)
            confidence_text = f"{confidence * 100:.1f}%"
            
            # Configurar texto
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            thickness = 2
            
            # Calcular tamaño del texto
            (text_width, text_height), _ = cv2.getTextSize(
                f"{emotion_text} ({confidence_text})", font, font_scale, thickness
            )
            
            # Fondo para el texto
            cv2.rectangle(
                image,
                (x, y - text_height - 10),
                (x + text_width, y),
                color,
                -1
            )
            
            # Texto
            cv2.putText(
                image,
                f"{emotion_text} ({confidence_text})",
                (x, y - 5),
                font,
                font_scale,
                (255, 255, 255),
                thickness
            )
        
        # Guardar imagen anotada
        if output_path is None:
            base_name, ext = os.path.splitext(image_path)
            output_path = f"{base_name}_annotated{ext}"
        
        cv2.imwrite(output_path, image)
        
        return output_path
        
    except Exception as e:
        print(f"Error al anotar imagen: {str(e)}")
        return image_path  # Retornar original si hay error


def get_emotion_color_hex(emotion):
    """
    Retorna el color hexadecimal para una emoción específica.
    
    Args:
        emotion: Nombre de la emoción
        
    Returns:
        str: Código de color hexadecimal
    """
    colors = {
        'neutral': '#808080',     # Gris
        'happiness': '#10B981',   # Verde
        'surprise': '#F59E0B',    # Amarillo
        'sadness': '#3B82F6',     # Azul
        'anger': '#EF4444',       # Rojo
        'disgust': '#84CC16',     # Verde lima
        'fear': '#8B5CF6',        # Púrpura
        'contempt': '#F97316'     # Naranja
    }
    return colors.get(emotion.lower(), '#6B7280')


def calculate_emotion_intensity(emotion_scores):
    """
    Calcula la intensidad general de las emociones.
    
    Args:
        emotion_scores: Diccionario con scores de emociones
        
    Returns:
        dict: Intensidades categorizadas
    """
    # Excluir neutral para calcular intensidad emocional
    emotional_scores = {k: v for k, v in emotion_scores.items() if k != 'neutral'}
    
    if not emotional_scores:
        return {'level': 'neutral', 'score': emotion_scores.get('neutral', 0)}
    
    max_emotion_score = max(emotional_scores.values())
    total_emotional_score = sum(emotional_scores.values())
    
    # Clasificar intensidad
    if max_emotion_score > 0.8:
        intensity_level = 'muy_alta'
    elif max_emotion_score > 0.6:
        intensity_level = 'alta'
    elif max_emotion_score > 0.4:
        intensity_level = 'media'
    elif max_emotion_score > 0.2:
        intensity_level = 'baja'
    else:
        intensity_level = 'muy_baja'
    
    return {
        'level': intensity_level,
        'score': max_emotion_score,
        'total_emotional': total_emotional_score,
        'dominant_emotion': max(emotional_scores, key=emotional_scores.get)
    }


def generate_emotion_report(analysis_results):
    """
    Genera un reporte textual del análisis de emociones.
    
    Args:
        analysis_results: Resultados del análisis
        
    Returns:
        str: Reporte en texto
    """
    if analysis_results.get('error'):
        return f"Error en el análisis: {analysis_results['error']}"
    
    faces_count = analysis_results.get('faces_detected', 0)
    
    if faces_count == 0:
        return "No se detectaron rostros en la imagen."
    
    report_lines = [
        f"=== REPORTE DE ANÁLISIS DE EMOCIONES ===",
        f"Rostros detectados: {faces_count}",
        ""
    ]
    
    faces_analysis = analysis_results.get('faces_analysis', [])
    
    for i, face in enumerate(faces_analysis, 1):
        emotion = face.get('dominant_emotion', 'unknown')
        confidence = face.get('confidence', 0)
        
        # Traducir emoción
        emotion_translations = {
            'neutral': 'Neutral',
            'happiness': 'Felicidad',
            'surprise': 'Sorpresa',
            'sadness': 'Tristeza',
            'anger': 'Ira',
            'disgust': 'Disgusto',
            'fear': 'Miedo',
            'contempt': 'Desprecio'
        }
        
        emotion_text = emotion_translations.get(emotion, emotion)
        
        report_lines.extend([
            f"Rostro {i}:",
            f"  - Emoción dominante: {emotion_text}",
            f"  - Confianza: {confidence * 100:.2f}%",
            ""
        ])
        
        # Mostrar todas las emociones si están disponibles
        all_emotions = face.get('all_emotions', {})
        if all_emotions:
            report_lines.append("  - Distribución completa:")
            for emo, score in sorted(all_emotions.items(), key=lambda x: x[1], reverse=True):
                emo_translated = emotion_translations.get(emo, emo)
                report_lines.append(f"    {emo_translated}: {score * 100:.2f}%")
            report_lines.append("")
    
    return "\n".join(report_lines)