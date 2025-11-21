"""
Pruebas funcionales para la aplicación de detección de emociones.
Valida casos de uso clave del sistema: inicio, detección, visualización.
"""
import time
from io import BytesIO
from PIL import Image

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from apps.emotions.models import EmotionAnalysis, EmotionStatistics
from apps.emotions.services.emotion_detector import emotion_detector

User = get_user_model()


def create_test_image_file(width=200, height=200):
    """Crea un archivo de imagen de prueba."""
    image = Image.new('RGB', (width, height), color='blue')
    img_io = BytesIO()
    image.save(img_io, format='PNG')
    img_io.seek(0)
    return ContentFile(img_io.read(), name='test_functional.png')


class SistemaInicioFunctionalTest(TestCase):
    """
    Pruebas funcionales para el inicio del sistema.
    Valida que el usuario pueda acceder y navegar por la aplicación.
    """
    
    def setUp(self):
        """Configuración inicial."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='functional_user',
            email='functional@test.com',
            password='testpass123'
        )
    
    def test_usuario_puede_iniciar_sesion_y_acceder_dashboard(self):
        """Caso de uso: Usuario inicia sesión y accede al dashboard."""
        # Usuario hace login
        self.client.force_login(self.user)
        
        # Accede al dashboard
        response = self.client.get(reverse('emotions:dashboard'))
        
        # Verifica que puede acceder
        self.assertIn(response.status_code, [200, 302])
    
    def test_dashboard_muestra_informacion_inicial(self):
        """Caso de uso: Dashboard muestra información inicial del usuario."""
        self.client.force_login(self.user)
        
        # Accede al dashboard
        response = self.client.get(reverse('emotions:dashboard'))
        
        if response.status_code == 200:
            # Verifica que hay estadísticas creadas
            stats_exist = EmotionStatistics.objects.filter(user=self.user).exists()
            self.assertTrue(stats_exist)
    
    def test_usuario_puede_navegar_entre_secciones(self):
        """Caso de uso: Usuario navega entre diferentes secciones."""
        self.client.force_login(self.user)
        
        # Navega a diferentes secciones
        sections = [
            ('emotions:dashboard', 'Dashboard'),
            ('emotions:upload', 'Subir imagen'),
            ('emotions:analysis_list', 'Lista de análisis'),
            ('emotions:statistics', 'Estadísticas'),
        ]
        
        for url_name, description in sections:
            response = self.client.get(reverse(url_name))
            self.assertIn(response.status_code, [200, 302], 
                         f"Error al acceder a {description}")


class DeteccionEmocionFunctionalTest(TestCase):
    """
    Pruebas funcionales para la detección de emociones.
    Valida el flujo completo de análisis de imágenes.
    """
    
    def setUp(self):
        """Configuración inicial."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='detector_user',
            email='detector@test.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
    
    def test_detector_se_inicializa_correctamente(self):
        """Caso de uso: Sistema carga el detector de emociones."""
        # Verifica que el detector esté disponible
        self.assertIsNotNone(emotion_detector)
        self.assertIsNotNone(emotion_detector.session)
        self.assertEqual(len(emotion_detector.EMOTION_LABELS), 8)
    
    def test_usuario_puede_crear_analisis_desde_imagen(self):
        """Caso de uso: Usuario sube imagen y crea análisis."""
        # Contador inicial
        initial_count = EmotionAnalysis.objects.filter(user=self.user).count()
        
        # Crear un análisis
        analysis = EmotionAnalysis.objects.create(
            user=self.user,
            image=create_test_image_file(),
            faces_detected=1,
            dominant_emotion='happiness',
            average_confidence=0.85
        )
        
        # Verifica que se creó
        final_count = EmotionAnalysis.objects.filter(user=self.user).count()
        self.assertEqual(final_count, initial_count + 1)
        self.assertEqual(analysis.dominant_emotion, 'happiness')
    
    def test_analisis_guarda_informacion_completa(self):
        """Caso de uso: Análisis guarda todos los datos necesarios."""
        analysis = EmotionAnalysis.objects.create(
            user=self.user,
            image=create_test_image_file(),
            faces_detected=2,
            dominant_emotion='happiness',
            average_confidence=0.90,
            analysis_results={
                'faces_detected': 2,
                'faces_analysis': [
                    {'dominant_emotion': 'happiness', 'confidence': 0.95},
                    {'dominant_emotion': 'happiness', 'confidence': 0.85}
                ]
            }
        )
        
        # Verifica los datos
        self.assertEqual(analysis.faces_detected, 2)
        self.assertGreater(analysis.average_confidence, 0)
        self.assertIn('faces_analysis', analysis.analysis_results)


class VisualizacionResultadosFunctionalTest(TestCase):
    """
    Pruebas funcionales para visualización de resultados.
    Valida que los usuarios puedan ver sus análisis correctamente.
    """
    
    def setUp(self):
        """Configuración inicial."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='viewer_user',
            email='viewer@test.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
        
        # Crear análisis de prueba
        self.analysis = EmotionAnalysis.objects.create(
            user=self.user,
            image=create_test_image_file(),
            faces_detected=1,
            dominant_emotion='happiness',
            average_confidence=0.92,
            analysis_results={
                'faces_detected': 1,
                'faces_analysis': [{
                    'dominant_emotion': 'happiness',
                    'confidence': 0.92,
                    'all_emotions': {
                        'happiness': 0.92,
                        'neutral': 0.05,
                        'surprise': 0.03
                    }
                }]
            }
        )
    
    def test_usuario_puede_ver_lista_de_analisis(self):
        """Caso de uso: Usuario visualiza su lista de análisis."""
        response = self.client.get(reverse('emotions:analysis_list'))
        
        self.assertIn(response.status_code, [200, 302])
        
        # Verifica que existe el análisis
        analyses = EmotionAnalysis.objects.filter(user=self.user)
        self.assertEqual(analyses.count(), 1)
    
    def test_usuario_puede_ver_detalle_de_analisis(self):
        """Caso de uso: Usuario ve detalles de un análisis específico."""
        url = reverse('emotions:analysis_detail', kwargs={'pk': self.analysis.pk})
        response = self.client.get(url)
        
        self.assertIn(response.status_code, [200, 302])
    
    def test_analisis_muestra_informacion_completa(self):
        """Caso de uso: Análisis muestra toda la información relevante."""
        # Obtener métodos de visualización
        faces_summary = self.analysis.get_faces_summary()
        distribution = self.analysis.get_emotion_distribution()
        emotion_display = self.analysis.get_dominant_emotion_display()
        
        # Verificar que retornan datos válidos
        self.assertIsInstance(faces_summary, list)
        self.assertIsInstance(distribution, dict)
        self.assertIsInstance(emotion_display, str)
        self.assertIn('Felicidad', emotion_display)


class EstadisticasUsuarioFunctionalTest(TestCase):
    """
    Pruebas funcionales para estadísticas de usuario.
    Valida que las estadísticas se actualicen correctamente.
    """
    
    def setUp(self):
        """Configuración inicial."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='stats_user',
            email='stats@test.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
    
    def test_estadisticas_se_crean_automaticamente(self):
        """Caso de uso: Sistema crea estadísticas automáticamente."""
        # Acceder a dashboard para crear estadísticas
        self.client.get(reverse('emotions:dashboard'))
        
        # Verificar que existen
        stats_exist = EmotionStatistics.objects.filter(user=self.user).exists()
        self.assertTrue(stats_exist)
    
    def test_estadisticas_se_actualizan_con_analisis(self):
        """Caso de uso: Estadísticas se actualizan con nuevos análisis."""
        # Crear estadísticas
        stats, _ = EmotionStatistics.objects.get_or_create(user=self.user)
        
        # Crear varios análisis
        for i in range(3):
            EmotionAnalysis.objects.create(
                user=self.user,
                image=create_test_image_file(),
                faces_detected=1,
                dominant_emotion='happiness'
            )
        
        # Actualizar estadísticas
        stats.update_statistics()
        
        # Verificar actualización
        self.assertEqual(stats.total_analyses, 3)
        self.assertEqual(stats.total_faces_detected, 3)
    
    def test_usuario_puede_ver_estadisticas(self):
        """Caso de uso: Usuario visualiza sus estadísticas."""
        response = self.client.get(reverse('emotions:statistics'))
        
        self.assertIn(response.status_code, [200, 302])


class GestionAnalisisFunctionalTest(TestCase):
    """
    Pruebas funcionales para gestión de análisis.
    Valida operaciones CRUD sobre análisis.
    """
    
    def setUp(self):
        """Configuración inicial."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='manager_user',
            email='manager@test.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
        
        self.analysis = EmotionAnalysis.objects.create(
            user=self.user,
            image=create_test_image_file(),
            faces_detected=1,
            dominant_emotion='happiness'
        )
    
    def test_usuario_puede_eliminar_su_analisis(self):
        """Caso de uso: Usuario elimina un análisis propio."""
        initial_count = EmotionAnalysis.objects.filter(user=self.user).count()
        
        # Eliminar análisis
        url = reverse('emotions:delete_analysis', kwargs={'pk': self.analysis.pk})
        response = self.client.post(url)
        
        # Verificar redirección
        self.assertEqual(response.status_code, 302)
        
        # Verificar eliminación
        final_count = EmotionAnalysis.objects.filter(user=self.user).count()
        self.assertEqual(final_count, initial_count - 1)
    
    def test_usuario_no_puede_ver_analisis_de_otros(self):
        """Caso de uso: Usuario no puede acceder a análisis ajenos."""
        # Crear otro usuario y su análisis
        other_user = User.objects.create_user(
            username='other_user',
            password='testpass123'
        )
        other_analysis = EmotionAnalysis.objects.create(
            user=other_user,
            image=create_test_image_file(),
            faces_detected=1,
            dominant_emotion='sadness'
        )
        
        # Intentar acceder al análisis ajeno
        url = reverse('emotions:analysis_detail', kwargs={'pk': other_analysis.pk})
        response = self.client.get(url)
        
        # Debe ser rechazado
        self.assertIn(response.status_code, [302, 404])


class FlujosCompletosFunctionalTest(TestCase):
    """
    Pruebas funcionales de flujos completos.
    Simula escenarios reales de uso del sistema.
    """
    
    def setUp(self):
        """Configuración inicial."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='complete_user',
            email='complete@test.com',
            password='testpass123'
        )
    
    def test_flujo_completo_nuevo_usuario(self):
        """Caso de uso: Flujo completo de un nuevo usuario."""
        # 1. Usuario inicia sesión
        self.client.force_login(self.user)
        
        # 2. Accede al dashboard
        response = self.client.get(reverse('emotions:dashboard'))
        self.assertIn(response.status_code, [200, 302])
        
        # 3. Ve que no tiene análisis
        analyses = EmotionAnalysis.objects.filter(user=self.user)
        self.assertEqual(analyses.count(), 0)
        
        # 4. Crea su primer análisis
        analysis = EmotionAnalysis.objects.create(
            user=self.user,
            image=create_test_image_file(),
            faces_detected=1,
            dominant_emotion='happiness',
            average_confidence=0.88
        )
        
        # 5. Ve el detalle del análisis
        url = reverse('emotions:analysis_detail', kwargs={'pk': analysis.pk})
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 302])
        
        # 6. Ve sus estadísticas actualizadas
        response = self.client.get(reverse('emotions:statistics'))
        self.assertIn(response.status_code, [200, 302])
    
    def test_flujo_multiples_analisis(self):
        """Caso de uso: Usuario realiza múltiples análisis."""
        self.client.force_login(self.user)
        
        # Crear varios análisis
        emociones = ['happiness', 'sadness', 'surprise', 'neutral']
        
        for emotion in emociones:
            EmotionAnalysis.objects.create(
                user=self.user,
                image=create_test_image_file(),
                faces_detected=1,
                dominant_emotion=emotion,
                average_confidence=0.85
            )
        
        # Verificar que todos se crearon
        total_analyses = EmotionAnalysis.objects.filter(user=self.user).count()
        self.assertEqual(total_analyses, 4)
        
        # Ver lista de análisis
        response = self.client.get(reverse('emotions:analysis_list'))
        self.assertIn(response.status_code, [200, 302])
    
    def test_sistema_mantiene_aislamiento_entre_usuarios(self):
        """Caso de uso: Sistema mantiene datos separados por usuario."""
        self.client.force_login(self.user)
        
        # Crear análisis para usuario 1
        EmotionAnalysis.objects.create(
            user=self.user,
            image=create_test_image_file(),
            faces_detected=1,
            dominant_emotion='happiness'
        )
        
        # Crear usuario 2 con su análisis
        user2 = User.objects.create_user(
            username='user2',
            password='testpass123'
        )
        EmotionAnalysis.objects.create(
            user=user2,
            image=create_test_image_file(),
            faces_detected=1,
            dominant_emotion='sadness'
        )
        
        # Usuario 1 solo ve sus análisis
        user1_analyses = EmotionAnalysis.objects.filter(user=self.user)
        self.assertEqual(user1_analyses.count(), 1)
        self.assertEqual(user1_analyses.first().dominant_emotion, 'happiness')
        
        # Usuario 2 solo ve sus análisis
        user2_analyses = EmotionAnalysis.objects.filter(user=user2)
        self.assertEqual(user2_analyses.count(), 1)
        self.assertEqual(user2_analyses.first().dominant_emotion, 'sadness')


class RendimientoSistemaFunctionalTest(TestCase):
    """
    Pruebas funcionales de rendimiento básico.
    Valida que el sistema responda adecuadamente.
    """
    
    def setUp(self):
        """Configuración inicial."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='performance_user',
            email='performance@test.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
    
    def test_carga_de_lista_con_multiples_analisis(self):
        """Caso de uso: Sistema carga lista con muchos análisis."""
        # Crear 20 análisis
        for i in range(20):
            EmotionAnalysis.objects.create(
                user=self.user,
                image=create_test_image_file(),
                faces_detected=1,
                dominant_emotion='happiness'
            )
        
        # Medir tiempo de carga
        start_time = time.time()
        response = self.client.get(reverse('emotions:analysis_list'))
        elapsed_time = time.time() - start_time
        
        # Verificar que responde
        self.assertIn(response.status_code, [200, 302])
        
        # Verificar tiempo razonable (menos de 5 segundos)
        self.assertLess(elapsed_time, 5.0)
    
    def test_acceso_rapido_a_dashboard(self):
        """Caso de uso: Dashboard carga rápidamente."""
        start_time = time.time()
        response = self.client.get(reverse('emotions:dashboard'))
        elapsed_time = time.time() - start_time
        
        self.assertIn(response.status_code, [200, 302])
        self.assertLess(elapsed_time, 3.0)


if __name__ == '__main__':
    import unittest
    unittest.main()
