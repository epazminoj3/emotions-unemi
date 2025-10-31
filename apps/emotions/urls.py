"""
URLs para la aplicación de detección de emociones.
"""
from django.urls import path
from .views import emotion_views, video_stream

app_name = 'emotions'

urlpatterns = [
    # Dashboard principal
    path('', emotion_views.emotion_dashboard, name='dashboard'),
    
    # Análisis de imágenes
    path('upload/', emotion_views.upload_analysis, name='upload'),
    path('quick/', emotion_views.quick_analysis, name='quick_analysis'),
    path('camera/', emotion_views.camera_analysis, name='camera_analysis'),
    
    # Análisis en tiempo real
    path('real-time/', video_stream.real_time_analysis, name='real_time'),
    path('video-feed/', video_stream.video_feed, name='video_feed'),
    
    # Gestión de análisis
    path('analysis/', emotion_views.analysis_list, name='analysis_list'),
    path('analysis/<int:pk>/', emotion_views.analysis_detail, name='analysis_detail'),
    path('analysis/<int:pk>/delete/', emotion_views.delete_analysis, name='delete_analysis'),
    
    # Estadísticas
    path('statistics/', emotion_views.user_statistics, name='statistics'),
    
    # API endpoints
    path('api/analyze-base64/', emotion_views.api_analyze_base64, name='api_analyze_base64'),
    path('api/save-camera-analysis/', emotion_views.api_save_camera_analysis, name='api_save_camera_analysis'),
    path('api/toggle-detection/', video_stream.toggle_detection, name='toggle_detection'),
    path('api/change-camera/', video_stream.change_camera, name='change_camera'),
    path('api/current-results/', video_stream.get_current_results, name='get_current_results'),
    path('api/release-camera/', video_stream.release_camera, name='release_camera'),
]