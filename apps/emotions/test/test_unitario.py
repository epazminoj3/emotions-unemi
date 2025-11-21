"""
Pruebas unitarias para la aplicación de detección de emociones.
Cubre funciones críticas del sistema: EmotionDetector, modelos y utilidades.
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
import os
import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from io import BytesIO
import cv2

from apps.emotions.models import EmotionAnalysis, EmotionStatistics
from apps.emotions.services.emotion_detector import EmotionDetector
from apps.emotions.utils.image_utils import (
    validate_image_file,
    calculate_emotion_intensity,
    get_emotion_color_hex
)

User = get_user_model()


class EmotionDetectorUnitTest(TestCase):
    """
    Pruebas unitarias para la clase EmotionDetector.
    Valida preprocesamiento, postprocesamiento y funciones auxiliares.
    """
    
    def setUp(self):
        """Configuración inicial para cada prueba."""
        self.detector = EmotionDetector()
    
    def test_emotion_labels_mapping(self):
        """Verifica que el mapeo de etiquetas de emociones esté completo."""
        expected_labels = {
            0: 'neutral', 1: 'happiness', 2: 'surprise', 3: 'sadness',
            4: 'anger', 5: 'disgust', 6: 'fear', 7: 'contempt'
        }
        self.assertEqual(self.detector.EMOTION_LABELS, expected_labels)
    
    def test_softmax_function(self):
        """Valida que la función softmax convierta scores a probabilidades."""
        scores = np.array([1.0, 2.0, 3.0])
        probabilities = self.detector.softmax(scores)
        
        self.assertAlmostEqual(probabilities.sum(), 1.0, places=5)
        self.assertTrue(np.all(probabilities >= 0))
        self.assertTrue(np.all(probabilities <= 1))
        self.assertTrue(probabilities[2] > probabilities[1] > probabilities[0])
    
    def test_softmax_numerical_stability(self):
        """Verifica estabilidad numérica con valores grandes."""
        scores = np.array([1000, 1001, 1002])
        probabilities = self.detector.softmax(scores)
        
        self.assertAlmostEqual(probabilities.sum(), 1.0, places=5)
        self.assertFalse(np.any(np.isnan(probabilities)))
        self.assertFalse(np.any(np.isinf(probabilities)))
    
    def test_preprocess_face_output_shape(self):
        """Verifica que el preprocesamiento genere el shape correcto."""
        face_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        processed = self.detector.preprocess_face(face_img)
        
        self.assertEqual(processed.shape, (1, 1, 64, 64))
    
    def test_preprocess_face_value_range(self):
        """Valida que los valores procesados estén en rango [0, 255]."""
        face_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        processed = self.detector.preprocess_face(face_img)
        
        self.assertTrue(np.all(processed >= 0))
        self.assertTrue(np.all(processed <= 255))
    
    def test_postprocess_prediction_structure(self):
        """Verifica que el postprocesamiento genere estructura correcta."""
        scores = np.random.randn(1, 8)
        result = self.detector.postprocess_prediction(scores)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 8)
        for emotion, prob in result.items():
            self.assertIn(emotion, self.detector.EMOTION_LABELS.values())
            self.assertGreaterEqual(prob, 0.0)
            self.assertLessEqual(prob, 1.0)
    
    def test_postprocess_prediction_probability_sum(self):
        """Valida que las probabilidades sumen aproximadamente 1."""
        scores = np.random.randn(1, 8)
        result = self.detector.postprocess_prediction(scores)
        
        total_prob = sum(result.values())
        self.assertAlmostEqual(total_prob, 1.0, places=5)
    
    def test_get_emotion_translation(self):
        """Verifica la traducción correcta de emociones."""
        translations = {
            'neutral': 'Neutral',
            'happiness': 'Felicidad',
            'sadness': 'Tristeza',
            'anger': 'Ira',
            'fear': 'Miedo'
        }
        
        for eng, esp in translations.items():
            self.assertEqual(self.detector.get_emotion_translation(eng), esp)
    
    def test_get_emotion_translation_unknown(self):
        """Verifica comportamiento con emoción desconocida."""
        result = self.detector.get_emotion_translation('unknown_emotion')
        self.assertEqual(result, 'Unknown_Emotion')


class EmotionAnalysisModelTest(TestCase):
    """
    Pruebas unitarias para el modelo EmotionAnalysis.
    Valida métodos de cálculo y transformación de datos.
    """
    
    def setUp(self):
        """Configuración inicial para cada prueba."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_get_emotion_translation(self):
        """Verifica traducción de emociones en el modelo."""
        analysis = EmotionAnalysis(user=self.user)
        
        self.assertEqual(analysis.get_emotion_translation('happiness'), 'Felicidad')
        self.assertEqual(analysis.get_emotion_translation('anger'), 'Ira')
        self.assertEqual(analysis.get_emotion_translation('fear'), 'Miedo')
    
    def test_get_emotion_distribution_no_results(self):
        """Valida comportamiento cuando no hay resultados."""
        analysis = EmotionAnalysis(
            user=self.user,
            analysis_results={}
        )
        
        result = analysis.get_emotion_distribution()
        self.assertEqual(result, {})
    
    def test_get_emotion_distribution_single_face(self):
        """Verifica distribución con un solo rostro."""
        analysis = EmotionAnalysis(
            user=self.user,
            analysis_results={
                'faces_analysis': [
                    {'dominant_emotion': 'happiness', 'confidence': 0.95}
                ]
            }
        )
        
        distribution = analysis.get_emotion_distribution()
        self.assertEqual(distribution['happiness'], 100.0)
    
    def test_get_emotion_distribution_multiple_faces(self):
        """Verifica distribución con múltiples rostros."""
        analysis = EmotionAnalysis(
            user=self.user,
            analysis_results={
                'faces_analysis': [
                    {'dominant_emotion': 'happiness', 'confidence': 0.95},
                    {'dominant_emotion': 'happiness', 'confidence': 0.90},
                    {'dominant_emotion': 'sadness', 'confidence': 0.85}
                ]
            }
        )
        
        distribution = analysis.get_emotion_distribution()
        self.assertAlmostEqual(distribution['happiness'], 66.67, places=1)
        self.assertAlmostEqual(distribution['sadness'], 33.33, places=1)
    
    def test_get_faces_summary_structure(self):
        """Valida estructura del resumen de rostros."""
        analysis = EmotionAnalysis(
            user=self.user,
            analysis_results={
                'faces_analysis': [
                    {
                        'dominant_emotion': 'happiness',
                        'confidence': 0.95,
                        'all_emotions': {
                            'happiness': 0.95,
                            'neutral': 0.03,
                            'surprise': 0.02
                        }
                    }
                ]
            }
        )
        
        summary = analysis.get_faces_summary()
        self.assertIsInstance(summary, list)
        self.assertEqual(len(summary), 1)
        self.assertIn('dominant_emotion', summary[0])
        self.assertIn('dominant_emotion_name', summary[0])
        self.assertIn('confidence', summary[0])


class EmotionStatisticsModelTest(TestCase):
    """
    Pruebas unitarias para el modelo EmotionStatistics.
    Valida cálculos estadísticos y agregaciones.
    """
    
    def setUp(self):
        """Configuración inicial para cada prueba."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.stats = EmotionStatistics.objects.create(user=self.user)
    
    def test_initial_statistics_values(self):
        """Verifica valores iniciales de estadísticas."""
        self.assertEqual(self.stats.total_analyses, 0)
        self.assertEqual(self.stats.total_faces_detected, 0)
        self.assertEqual(self.stats.neutral_count, 0)
        self.assertEqual(self.stats.happiness_count, 0)
    
    def test_get_emotion_distribution_dict_empty(self):
        """Valida distribución cuando no hay datos."""
        distribution = self.stats.get_emotion_distribution_dict()
        
        self.assertIsInstance(distribution, dict)
        for emotion, percentage in distribution.items():
            self.assertEqual(percentage, 0.0)
    
    def test_get_emotion_distribution_dict_with_data(self):
        """Verifica cálculo de distribución con datos."""
        self.stats.happiness_count = 50
        self.stats.sadness_count = 30
        self.stats.anger_count = 20
        self.stats.save()
        
        distribution = self.stats.get_emotion_distribution_dict()
        
        self.assertAlmostEqual(distribution['Felicidad'], 50.0, places=1)
        self.assertAlmostEqual(distribution['Tristeza'], 30.0, places=1)
        self.assertAlmostEqual(distribution['Ira'], 20.0, places=1)


class ImageUtilsTest(TestCase):
    """
    Pruebas unitarias para utilidades de procesamiento de imágenes.
    Valida funciones auxiliares de validación y transformación.
    """
    
    def create_test_image(self, width=200, height=200, format='PNG'):
        """Crea una imagen de prueba en memoria."""
        image = Image.new('RGB', (width, height), color='red')
        img_io = BytesIO()
        image.save(img_io, format=format)
        img_io.seek(0)
        return img_io
    
    def test_validate_image_file_valid_png(self):
        """Verifica validación exitosa de imagen PNG."""
        img_io = self.create_test_image(format='PNG')
        is_valid, error = validate_image_file(img_io)
        
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_validate_image_file_valid_jpeg(self):
        """Verifica validación exitosa de imagen JPEG."""
        img_io = self.create_test_image(format='JPEG')
        is_valid, error = validate_image_file(img_io)
        
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_validate_image_file_too_small(self):
        """Verifica rechazo de imagen muy pequeña."""
        img_io = self.create_test_image(width=32, height=32)
        is_valid, error = validate_image_file(img_io)
        
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
    
    def test_validate_image_file_too_large(self):
        """Verifica rechazo de imagen muy grande."""
        img_io = self.create_test_image(width=5000, height=5000)
        is_valid, error = validate_image_file(img_io)
        
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
    
    def test_get_emotion_color_hex_valid(self):
        """Verifica colores hexadecimales para emociones."""
        self.assertEqual(get_emotion_color_hex('happiness'), '#10B981')
        self.assertEqual(get_emotion_color_hex('anger'), '#EF4444')
        self.assertEqual(get_emotion_color_hex('sadness'), '#3B82F6')
        self.assertEqual(get_emotion_color_hex('neutral'), '#808080')
    
    def test_get_emotion_color_hex_unknown(self):
        """Verifica color por defecto para emoción desconocida."""
        result = get_emotion_color_hex('unknown_emotion')
        self.assertEqual(result, '#6B7280')
    
    def test_calculate_emotion_intensity_neutral(self):
        """Verifica cálculo de intensidad para estado neutral."""
        scores = {'neutral': 0.95, 'happiness': 0.03, 'sadness': 0.02}
        result = calculate_emotion_intensity(scores)
        
        self.assertIn(result['level'], ['neutral', 'muy_baja'])
    
    def test_calculate_emotion_intensity_very_high(self):
        """Verifica clasificación de intensidad muy alta."""
        scores = {'happiness': 0.9, 'neutral': 0.1}
        result = calculate_emotion_intensity(scores)
        
        self.assertEqual(result['level'], 'muy_alta')
        self.assertGreater(result['score'], 0.8)
    
    def test_calculate_emotion_intensity_high(self):
        """Verifica clasificación de intensidad alta."""
        scores = {'anger': 0.7, 'neutral': 0.3}
        result = calculate_emotion_intensity(scores)
        
        self.assertEqual(result['level'], 'alta')
        self.assertGreater(result['score'], 0.6)
    
    def test_calculate_emotion_intensity_medium(self):
        """Verifica clasificación de intensidad media."""
        scores = {'sadness': 0.5, 'neutral': 0.5}
        result = calculate_emotion_intensity(scores)
        
        self.assertEqual(result['level'], 'media')
    
    def test_calculate_emotion_intensity_dominant_emotion(self):
        """Verifica identificación de emoción dominante."""
        scores = {'happiness': 0.6, 'surprise': 0.2, 'neutral': 0.2}
        result = calculate_emotion_intensity(scores)
        
        self.assertEqual(result['dominant_emotion'], 'happiness')


class EmotionDetectorIntegrationTest(TestCase):
    """
    Pruebas de integración para EmotionDetector con datos simulados.
    Valida flujo completo de detección sin dependencias externas.
    """
    
    def setUp(self):
        """Configuración inicial para cada prueba."""
        self.detector = EmotionDetector()
    
    @patch('apps.emotions.services.emotion_detector.ort.InferenceSession')
    def test_predict_emotion_with_mock_session(self, mock_inference):
        """Verifica predicción de emoción con sesión simulada."""
        mock_output = np.array([[2.0, 5.0, 1.0, 0.5, 0.3, 0.2, 0.1, 0.0]])
        mock_session = MagicMock()
        mock_session.run.return_value = [mock_output]
        mock_inference.return_value = mock_session
        
        detector = EmotionDetector()
        face_img = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
        result = detector.predict_emotion(face_img)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 8)
        self.assertIn('happiness', result)
    
    def test_analyze_frame_empty_frame(self):
        """Verifica análisis de frame vacío."""
        empty_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        with patch.object(self.detector, 'detect_faces', return_value=[]):
            result = self.detector.analyze_frame(empty_frame)
            
            self.assertEqual(result['faces_detected'], 0)
            self.assertEqual(len(result.get('faces', [])), 0)
    
    @patch.object(EmotionDetector, 'detect_faces')
    @patch.object(EmotionDetector, 'predict_emotion')
    def test_analyze_frame_with_face(self, mock_predict, mock_detect):
        """Verifica análisis completo de frame con rostro."""
        mock_detect.return_value = [(100, 100, 150, 150)]
        mock_predict.return_value = {
            'happiness': 0.8,
            'neutral': 0.1,
            'sadness': 0.05,
            'anger': 0.05
        }
        
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        result = self.detector.analyze_frame(frame)
        
        self.assertEqual(result['faces_detected'], 1)
        self.assertEqual(len(result['faces']), 1)
        self.assertIn('emotions', result['faces'][0])


if __name__ == '__main__':
    unittest.main()
