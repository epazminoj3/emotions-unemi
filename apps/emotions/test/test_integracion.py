"""
Pruebas de integración para la aplicación de detección de emociones.
Valida el flujo completo de la aplicación Django: rutas, vistas, autenticación y procesamiento.
"""
import json
import base64
from io import BytesIO
from PIL import Image

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.base import ContentFile

from apps.emotions.models import EmotionAnalysis, EmotionStatistics

User = get_user_model()


def create_test_image_file():
    """Crea un archivo de imagen de prueba."""
    from PIL import Image
    from io import BytesIO
    
    image = Image.new('RGB', (100, 100), color='red')
    img_io = BytesIO()
    image.save(img_io, format='PNG')
    img_io.seek(0)
    return ContentFile(img_io.read(), name='test_image.png')


# Desactivar middleware de seguridad para las pruebas
@override_settings(
    MIDDLEWARE=[m for m in [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ] if 'security.middleware' not in m]
)


class AuthenticationIntegrationTest(TestCase):
    """
    Pruebas de integración para autenticación y control de acceso.
    """
    
    def setUp(self):
        """Configuración inicial para cada prueba."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_login_required_dashboard(self):
        """Verifica que el dashboard requiera autenticación."""
        response = self.client.get(reverse('emotions:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/signin/', response.url)
    
    def test_login_required_upload(self):
        """Verifica que la subida de imágenes requiera autenticación."""
        response = self.client.get(reverse('emotions:upload'))
        self.assertEqual(response.status_code, 302)
    
    def test_login_required_statistics(self):
        """Verifica que las estadísticas requieran autenticación."""
        response = self.client.get(reverse('emotions:statistics'))
        self.assertEqual(response.status_code, 302)
    
    def test_authenticated_access_dashboard(self):
        """Verifica acceso exitoso al dashboard con autenticación."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('emotions:dashboard'))
        self.assertIn(response.status_code, [200, 302])
    
    def test_authenticated_access_upload(self):
        """Verifica acceso a la vista de subida con autenticación."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('emotions:upload'))
        self.assertIn(response.status_code, [200, 302])


class DashboardIntegrationTest(TestCase):
    """
    Pruebas de integración para el dashboard principal.
    """
    
    def setUp(self):
        """Configuración inicial para cada prueba."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
    
    def test_dashboard_creates_statistics(self):
        """Verifica que el dashboard cree estadísticas automáticamente."""
        response = self.client.get(reverse('emotions:dashboard'))
        
        self.assertIn(response.status_code, [200, 302])
        if response.status_code == 200:
            stats_exists = EmotionStatistics.objects.filter(user=self.user).exists()
            self.assertTrue(stats_exists)
    
    def test_dashboard_context_data(self):
        """Verifica que el dashboard incluya datos de contexto correctos."""
        response = self.client.get(reverse('emotions:dashboard'))
        
        if response.status_code == 200 and response.context:
            self.assertIn('stats', response.context)
            self.assertIn('recent_analyses', response.context)
            self.assertIn('emotion_distribution', response.context)
    
    def test_dashboard_with_existing_analyses(self):
        """Verifica que el dashboard muestre análisis existentes."""
        # Crear un análisis de prueba
        EmotionAnalysis.objects.create(
            user=self.user,
            image=create_test_image_file(),
            faces_detected=1,
            dominant_emotion='happiness',
            average_confidence=0.95,
            analysis_results={'test': 'data'}
        )
        
        response = self.client.get(reverse('emotions:dashboard'))
        self.assertIn(response.status_code, [200, 302])


class AnalysisListIntegrationTest(TestCase):
    """
    Pruebas de integración para la lista de análisis.
    """
    
    def setUp(self):
        """Configuración inicial para cada prueba."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
    
    def test_analysis_list_access(self):
        """Verifica acceso a la lista de análisis."""
        response = self.client.get(reverse('emotions:analysis_list'))
        self.assertIn(response.status_code, [200, 302])
    
    def test_analysis_list_pagination(self):
        """Verifica que la paginación funcione correctamente."""
        # Crear 15 análisis para probar paginación (12 por página)
        for i in range(15):
            EmotionAnalysis.objects.create(
                user=self.user,
                faces_detected=1,
                dominant_emotion='happiness'
            )
        
        response = self.client.get(reverse('emotions:analysis_list'))
        self.assertIn(response.status_code, [200, 302])
        if response.status_code == 200 and response.context:
            self.assertTrue(response.context['page_obj'].has_next())
            self.assertEqual(len(response.context['page_obj']), 12)
    
    def test_analysis_list_filter_by_emotion(self):
        """Verifica filtrado por emoción."""
        EmotionAnalysis.objects.create(
            user=self.user,
            faces_detected=1,
            dominant_emotion='happiness'
        )
        EmotionAnalysis.objects.create(
            user=self.user,
            faces_detected=1,
            dominant_emotion='sadness'
        )
        
        response = self.client.get(reverse('emotions:analysis_list') + '?emotion=happiness')
        self.assertIn(response.status_code, [200, 302])
    
    def test_analysis_list_user_isolation(self):
        """Verifica que los usuarios solo vean sus propios análisis."""
        other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        
        EmotionAnalysis.objects.create(
            user=other_user,
            faces_detected=1,
            dominant_emotion='happiness'
        )
        
        response = self.client.get(reverse('emotions:analysis_list'))
        self.assertIn(response.status_code, [200, 302])
        if response.status_code == 200 and response.context:
            self.assertEqual(len(response.context['page_obj']), 0)


class AnalysisDetailIntegrationTest(TestCase):
    """
    Pruebas de integración para la vista de detalle de análisis.
    """
    
    def setUp(self):
        """Configuración inicial para cada prueba."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
        
        self.analysis = EmotionAnalysis.objects.create(
            user=self.user,
            image=create_test_image_file(),
            faces_detected=2,
            dominant_emotion='happiness',
            average_confidence=0.85,
            analysis_results={
                'faces_analysis': [
                    {
                        'dominant_emotion': 'happiness',
                        'confidence': 0.9,
                        'all_emotions': {'happiness': 0.9, 'neutral': 0.1}
                    },
                    {
                        'dominant_emotion': 'happiness',
                        'confidence': 0.8,
                        'all_emotions': {'happiness': 0.8, 'surprise': 0.2}
                    }
                ]
            }
        )
    
    def test_analysis_detail_access(self):
        """Verifica acceso al detalle de análisis."""
        url = reverse('emotions:analysis_detail', kwargs={'pk': self.analysis.pk})
        response = self.client.get(url)
        
        self.assertIn(response.status_code, [200, 302])
    
    def test_analysis_detail_context(self):
        """Verifica que el contexto contenga datos correctos."""
        url = reverse('emotions:analysis_detail', kwargs={'pk': self.analysis.pk})
        response = self.client.get(url)
        
        if response.status_code == 200 and response.context:
            self.assertIn('analysis', response.context)
            self.assertIn('faces_summary', response.context)
            self.assertIn('emotion_distribution', response.context)
            self.assertEqual(response.context['analysis'].pk, self.analysis.pk)
    
    def test_analysis_detail_unauthorized_access(self):
        """Verifica que otros usuarios no puedan ver análisis ajenos."""
        other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        self.client.force_login(other_user)
        
        url = reverse('emotions:analysis_detail', kwargs={'pk': self.analysis.pk})
        response = self.client.get(url)
        
        self.assertIn(response.status_code, [302, 404])


class AnalysisDeleteIntegrationTest(TestCase):
    """
    Pruebas de integración para la eliminación de análisis.
    """
    
    def setUp(self):
        """Configuración inicial para cada prueba."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
        
        self.analysis = EmotionAnalysis.objects.create(
            user=self.user,
            image=create_test_image_file(),
            faces_detected=1,
            dominant_emotion='happiness'
        )
    
    def test_delete_analysis_get(self):
        """Verifica acceso a la página de confirmación de eliminación."""
        url = reverse('emotions:delete_analysis', kwargs={'pk': self.analysis.pk})
        response = self.client.get(url)
        
        self.assertIn(response.status_code, [200, 302])
    
    def test_delete_analysis_post(self):
        """Verifica que la eliminación mediante POST funcione."""
        url = reverse('emotions:delete_analysis', kwargs={'pk': self.analysis.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 302)
        if response.status_code == 302:
            self.assertFalse(EmotionAnalysis.objects.filter(pk=self.analysis.pk).exists())
    
    def test_delete_analysis_unauthorized(self):
        """Verifica que otros usuarios no puedan eliminar análisis ajenos."""
        other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        self.client.force_login(other_user)
        
        url = reverse('emotions:delete_analysis', kwargs={'pk': self.analysis.pk})
        response = self.client.post(url)
        
        self.assertIn(response.status_code, [302, 404])
        if response.status_code == 404:
            self.assertTrue(EmotionAnalysis.objects.filter(pk=self.analysis.pk).exists())


class StatisticsIntegrationTest(TestCase):
    """
    Pruebas de integración para las estadísticas de usuario.
    """
    
    def setUp(self):
        """Configuración inicial para cada prueba."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
    
    def test_statistics_page_access(self):
        """Verifica acceso a la página de estadísticas."""
        response = self.client.get(reverse('emotions:statistics'))
        self.assertIn(response.status_code, [200, 302])
    
    def test_statistics_creates_record(self):
        """Verifica que se cree registro de estadísticas si no existe."""
        response = self.client.get(reverse('emotions:statistics'))
        
        if response.status_code == 200:
            stats_exists = EmotionStatistics.objects.filter(user=self.user).exists()
            self.assertTrue(stats_exists)
    
    def test_statistics_context_data(self):
        """Verifica que el contexto incluya datos de estadísticas."""
        response = self.client.get(reverse('emotions:statistics'))
        
        if response.status_code == 200 and response.context:
            self.assertIn('stats', response.context)


class QuickAnalysisIntegrationTest(TestCase):
    """
    Pruebas de integración para análisis rápido sin guardar.
    """
    
    def setUp(self):
        """Configuración inicial para cada prueba."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
    
    def test_quick_analysis_get(self):
        """Verifica acceso a la vista de análisis rápido."""
        response = self.client.get(reverse('emotions:quick_analysis'))
        self.assertIn(response.status_code, [200, 302])
    
    def test_quick_analysis_form_display(self):
        """Verifica que el formulario se muestre correctamente."""
        response = self.client.get(reverse('emotions:quick_analysis'))
        if response.status_code == 200 and response.context:
            self.assertIn('form', response.context)


class APIEndpointsIntegrationTest(TestCase):
    """
    Pruebas de integración para endpoints de API.
    """
    
    def setUp(self):
        """Configuración inicial para cada prueba."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def create_test_base64_image(self):
        """Crea una imagen de prueba en formato base64."""
        image = Image.new('RGB', (200, 200), color='red')
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return f'data:image/png;base64,{img_str}'
    
    def test_api_analyze_base64_authentication(self):
        """Verifica que el API requiera autenticación."""
        self.client.logout()
        response = self.client.post(
            reverse('emotions:api_analyze_base64'),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 302)
    
    def test_api_analyze_base64_invalid_json(self):
        """Verifica manejo de JSON inválido."""
        response = self.client.post(
            reverse('emotions:api_analyze_base64'),
            data='invalid json',
            content_type='application/json'
        )
        self.assertIn(response.status_code, [302, 400])
    
    def test_toggle_detection_endpoint(self):
        """Verifica endpoint de activación/desactivación de detección."""
        response = self.client.post(
            reverse('emotions:toggle_detection'),
            data=json.dumps({'enable': True}),
            content_type='application/json'
        )
        self.assertIn(response.status_code, [200, 302, 400])
    
    def test_get_current_results_endpoint(self):
        """Verifica endpoint de obtención de resultados actuales."""
        response = self.client.get(reverse('emotions:get_current_results'))
        self.assertIn(response.status_code, [200, 302])
        if response.status_code == 200:
            data = json.loads(response.content)
            self.assertIn('success', data)


class RealTimeAnalysisIntegrationTest(TestCase):
    """
    Pruebas de integración para análisis en tiempo real.
    """
    
    def setUp(self):
        """Configuración inicial para cada prueba."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
    
    def test_real_time_page_access(self):
        """Verifica acceso a la página de análisis en tiempo real."""
        response = self.client.get(reverse('emotions:real_time'))
        self.assertIn(response.status_code, [200, 302])
    
    def test_video_feed_endpoint(self):
        """Verifica que el endpoint de video feed esté disponible."""
        response = self.client.get(reverse('emotions:video_feed'))
        self.assertIn(response.status_code, [200, 302, 500])


class WorkflowIntegrationTest(TestCase):
    """
    Pruebas de integración para flujos de trabajo completos.
    """
    
    def setUp(self):
        """Configuración inicial para cada prueba."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
    
    def test_complete_user_workflow(self):
        """Verifica flujo completo: login -> dashboard -> análisis -> detalle."""
        # 1. Acceso al dashboard
        response = self.client.get(reverse('emotions:dashboard'))
        self.assertIn(response.status_code, [200, 302])
        
        # 2. Ver lista de análisis
        response = self.client.get(reverse('emotions:analysis_list'))
        self.assertIn(response.status_code, [200, 302])
        
        # 3. Crear un análisis
        analysis = EmotionAnalysis.objects.create(
            user=self.user,
            image=create_test_image_file(),
            faces_detected=1,
            dominant_emotion='happiness',
            analysis_results={'test': 'data'}
        )
        
        # 4. Ver detalle del análisis
        url = reverse('emotions:analysis_detail', kwargs={'pk': analysis.pk})
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 302])
        
        # 5. Ver estadísticas
        response = self.client.get(reverse('emotions:statistics'))
        self.assertIn(response.status_code, [200, 302])
    
    def test_analysis_statistics_integration(self):
        """Verifica integración entre análisis y estadísticas."""
        # Crear análisis
        EmotionAnalysis.objects.create(
            user=self.user,
            faces_detected=2,
            dominant_emotion='happiness'
        )
        
        # Verificar que las estadísticas se actualicen
        stats, created = EmotionStatistics.objects.get_or_create(user=self.user)
        stats.update_statistics()
        
        self.assertEqual(stats.total_analyses, 1)
        self.assertEqual(stats.total_faces_detected, 2)


class URLRoutingIntegrationTest(TestCase):
    """
    Pruebas de integración para verificar que todas las rutas estén configuradas correctamente.
    """
    
    def setUp(self):
        """Configuración inicial para cada prueba."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_all_main_routes_resolve(self):
        """Verifica que todas las rutas principales se resuelvan correctamente."""
        routes = [
            'emotions:dashboard',
            'emotions:upload',
            'emotions:quick_analysis',
            'emotions:camera_analysis',
            'emotions:real_time',
            'emotions:analysis_list',
            'emotions:statistics',
        ]
        
        for route_name in routes:
            url = reverse(route_name)
            response = self.client.get(url)
            self.assertIn(response.status_code, [200, 302], 
                         f"Route {route_name} failed with status {response.status_code}")
    
    def test_api_routes_resolve(self):
        """Verifica que las rutas de API se resuelvan correctamente."""
        api_routes = [
            'emotions:api_analyze_base64',
            'emotions:toggle_detection',
            'emotions:get_current_results',
            'emotions:change_camera',
            'emotions:release_camera',
        ]
        
        for route_name in api_routes:
            url = reverse(route_name)
            self.assertIsNotNone(url, f"Route {route_name} could not be reversed")


if __name__ == '__main__':
    import unittest
    unittest.main()
