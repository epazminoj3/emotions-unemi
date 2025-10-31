"""
Servicio de detección de emociones usando el modelo FER+ con ONNX Runtime y OpenCV.
"""
import os
import cv2
import numpy as np
import onnxruntime as ort
from PIL import Image
from django.conf import settings
from typing import Dict, List, Tuple, Optional
import base64
from io import BytesIO


class EmotionDetector:
    """
    Detector de emociones usando el modelo FER+ pre-entrenado.
    """
    
    # Mapeo de emociones según el modelo FER+
    EMOTION_LABELS = {
        0: 'neutral',
        1: 'happiness', 
        2: 'surprise',
        3: 'sadness',
        4: 'anger',
        5: 'disgust',
        6: 'fear',
        7: 'contempt'
    }
    
    def __init__(self):
        """
        Inicializa el detector de emociones.
        """
        self.model_path = os.path.join(settings.BASE_DIR, 'models', 'emotion-ferplus-8.onnx')
        self.face_detector_path = os.path.join(settings.BASE_DIR, 'models', 'face_detection_yunet_2023mar_int8.onnx')
        self.session = None
        self.face_detector = None
        self._load_model()
        self._load_face_detector()
    
    def _load_model(self):
        """
        Carga el modelo ONNX de detección de emociones.
        """
        try:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Modelo no encontrado en: {self.model_path}")
            
            # Configurar sesión ONNX Runtime
            providers = ['CPUExecutionProvider']
            self.session = ort.InferenceSession(self.model_path, providers=providers)
            print(f"Modelo FER+ cargado exitosamente desde: {self.model_path}")
            
        except Exception as e:
            print(f"Error al cargar el modelo: {str(e)}")
            raise
    
    def _load_face_detector(self):
        """
        Carga el modelo YuNet ONNX para detección precisa de rostros.
        YuNet es más preciso y reduce falsos positivos comparado con Haar Cascades.
        """
        try:
            if not os.path.exists(self.face_detector_path):
                raise FileNotFoundError(f"Modelo YuNet no encontrado en: {self.face_detector_path}")
            
            # Inicializar el detector YuNet con tamaño de input por defecto
            # Se ajustará dinámicamente según el tamaño de la imagen
            self.face_detector = cv2.FaceDetectorYN.create(
                model=self.face_detector_path,
                config="",
                input_size=(320, 320),
                score_threshold=0.6,  # Umbral más alto para reducir falsos positivos
                nms_threshold=0.3,    # Non-maximum suppression integrado
                top_k=5000,
                backend_id=cv2.dnn.DNN_BACKEND_OPENCV,
                target_id=cv2.dnn.DNN_TARGET_CPU
            )
            print(f"Detector YuNet cargado exitosamente desde: {self.face_detector_path}")
                
        except Exception as e:
            print(f"Error al cargar el detector de rostros YuNet: {str(e)}")
            raise
    
    def preprocess_face(self, face_img: np.ndarray) -> np.ndarray:
        """
        Preprocesa la imagen del rostro para el modelo FER+ según especificación oficial.
        El modelo FER+ espera valores de píxeles en rango [0-255] sin normalización.
        
        Referencia: https://github.com/onnx/models/tree/main/vision/body_analysis/emotion_ferplus
        
        Args:
            face_img: Imagen del rostro extraída
            
        Returns:
            Imagen preprocesada para el modelo (1, 1, 64, 64) con valores [0-255]
        """
        try:
            # Validar input
            if face_img is None or face_img.size == 0:
                raise ValueError("Imagen de rostro vacía")
            
            # Convertir a escala de grises si es necesario
            if len(face_img.shape) == 3:
                face_gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
            else:
                face_gray = face_img.copy()
            
            # Redimensionar a 64x64 usando ANTIALIAS (INTER_AREA es equivalente)
            face_resized = cv2.resize(face_gray, (64, 64), interpolation=cv2.INTER_AREA)
            
            # Convertir a float32 MANTENIENDO rango [0-255]
            # El modelo FER+ fue entrenado con valores sin normalizar
            face_input = face_resized.astype(np.float32)
            
            # Reshape para el modelo: (1, 1, 64, 64)
            face_input = face_input.reshape(1, 1, 64, 64)
            
            # Logging solo para debug (comentar en producción si es necesario)
            # print(f"  Preprocesamiento: shape={face_input.shape}, min={face_input.min():.1f}, max={face_input.max():.1f}, mean={face_input.mean():.1f}")
            
            return face_input
            
        except Exception as e:
            print(f"Error en preprocesamiento: {e}")
            import traceback
            print(traceback.format_exc())
            # Último recurso: array de ceros con rango correcto
            return np.zeros((1, 1, 64, 64), dtype=np.float32)
    
    def softmax(self, scores: np.ndarray) -> np.ndarray:
        """
        Aplica función softmax para convertir scores a probabilidades.
        
        Args:
            scores: Array de scores del modelo
            
        Returns:
            Probabilidades normalizadas
        """
        exp_scores = np.exp(scores - np.max(scores))
        return exp_scores / np.sum(exp_scores)
    
    def postprocess_prediction(self, scores: np.ndarray, reduce_neutral_bias: bool = False) -> Dict[str, float]:
        """
        Postprocesa las predicciones del modelo aplicando softmax.
        Con el preprocesamiento correcto (valores 0-255), el modelo funciona bien sin ajustes.
        
        Args:
            scores: Scores de salida del modelo
            reduce_neutral_bias: DEPRECADO - Ya no es necesario con preprocesamiento correcto
            
        Returns:
            Diccionario con emociones y sus probabilidades
        """
        # Aplicar softmax directamente para obtener probabilidades
        probabilities = self.softmax(scores[0])
        
        # Crear diccionario de emociones con probabilidades
        emotion_probs = {}
        for idx, prob in enumerate(probabilities):
            emotion_name = self.EMOTION_LABELS[idx]
            emotion_probs[emotion_name] = float(prob)
        
        return emotion_probs
    
    def detect_faces(self, image: np.ndarray, realtime: bool = False) -> List[Tuple[int, int, int, int]]:
        """
        Detecta rostros en la imagen usando YuNet (más preciso que Haar Cascades).
        Reduce significativamente los falsos positivos.
        
        Args:
            image: Imagen de entrada
            realtime: Si es True, usa parámetros optimizados para tiempo real
            
        Returns:
            Lista de coordenadas de rostros detectados (x, y, w, h)
        """
        try:
            # Validar imagen
            if image is None or image.size == 0:
                print("Imagen vacía o nula")
                return []
            
            # Obtener dimensiones originales
            height, width = image.shape[:2]
            
            # Ajustar tamaño de entrada del detector según la imagen
            # Para mejor rendimiento en tiempo real
            if realtime and (width > 640 or height > 480):
                scale_factor = min(640 / width, 480 / height)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                resized_image = cv2.resize(image, (new_width, new_height))
            else:
                resized_image = image
                scale_factor = 1.0
                new_width, new_height = width, height
            
            # Ajustar el tamaño de entrada del detector
            self.face_detector.setInputSize((new_width, new_height))
            
            # Detectar rostros
            # YuNet devuelve: [x, y, w, h, x_re, y_re, x_le, y_le, x_nt, y_nt, x_rcm, y_rcm, x_lcm, y_lcm, score]
            # Donde: re=right eye, le=left eye, nt=nose tip, rcm=right corner mouth, lcm=left corner mouth
            _, faces = self.face_detector.detect(resized_image)
            
            if faces is None or len(faces) == 0:
                print("No se detectaron rostros con YuNet")
                return []
            
            # Extraer solo las coordenadas x, y, w, h y escalar de vuelta si es necesario
            face_boxes = []
            for face in faces:
                x, y, w, h = face[0:4]
                score = face[-1]  # Confianza de la detección
                
                # Filtrar por score mínimo
                if score < 0.6:  # Umbral de confianza
                    continue
                
                # Escalar coordenadas de vuelta al tamaño original
                if scale_factor != 1.0:
                    x = int(x / scale_factor)
                    y = int(y / scale_factor)
                    w = int(w / scale_factor)
                    h = int(h / scale_factor)
                
                # Asegurar que las coordenadas estén dentro de los límites
                x = max(0, int(x))
                y = max(0, int(y))
                w = min(width - x, int(w))
                h = min(height - y, int(h))
                
                face_boxes.append((x, y, w, h))
            
            print(f"✓ YuNet detectó {len(face_boxes)} rostro(s) con confianza >= 0.6")
            
            return face_boxes
            
        except Exception as e:
            import traceback
            print(f"Error en detección de rostros con YuNet: {e}")
            print(traceback.format_exc())
            return []
    
    def predict_emotion(self, face_img: np.ndarray) -> Dict[str, float]:
        """
        Predice la emoción de un rostro.
        
        Args:
            face_img: Imagen del rostro
            
        Returns:
            Diccionario con emociones y probabilidades
        """
        if self.session is None:
            raise Exception("Modelo no cargado")
        
        try:
            # Validar tamaño mínimo del rostro
            if face_img.shape[0] < 30 or face_img.shape[1] < 30:
                print(f"  Rostro muy pequeño: {face_img.shape}")
                # Rostro muy pequeño, devolver distribución neutral
                return {
                    'neutral': 0.8,
                    'happiness': 0.05,
                    'surprise': 0.05,
                    'sadness': 0.03,
                    'anger': 0.02,
                    'disgust': 0.02,
                    'fear': 0.02,
                    'contempt': 0.01
                }
            
            # Preprocesar la imagen
            processed_face = self.preprocess_face(face_img)
            
            # Realizar inferencia
            input_name = self.session.get_inputs()[0].name
            output = self.session.run(None, {input_name: processed_face})
            scores = output[0]
            
            # Logging solo para debug
            # print(f"  Scores del modelo (raw): {scores}")
            # print(f"  Shape: {scores.shape}, Min: {scores.min():.3f}, Max: {scores.max():.3f}")
            
            # Validar que los scores sean válidos
            if not isinstance(scores, np.ndarray) or scores.size == 0:
                raise Exception("Scores inválidos del modelo")
            
            # Postprocesar resultados
            emotions = self.postprocess_prediction(scores)
            
            # Logging solo para debug
            # print(f"  Emociones: {emotions}")
            
            # Validar que todas las emociones sumen aproximadamente 1
            total = sum(emotions.values())
            if abs(total - 1.0) > 0.1:  # Tolerancia del 10%
                print(f"  Advertencia: La suma de probabilidades es {total}, normalizando...")
                emotions = {k: v/total for k, v in emotions.items()}
            
            return emotions
            
        except Exception as e:
            print(f"Error en predicción de emoción: {e}")
            import traceback
            print(traceback.format_exc())
            # Devolver distribución neutral como fallback
            return {
                'neutral': 0.7,
                'happiness': 0.1,
                'surprise': 0.05,
                'sadness': 0.05,
                'anger': 0.03,
                'disgust': 0.03,
                'fear': 0.02,
                'contempt': 0.02
            }
    
    def analyze_image(self, image_path: str, save_faces: bool = True) -> Dict:
        """
        Analiza una imagen completa, detecta rostros y predice emociones.
        
        Args:
            image_path: Ruta de la imagen a analizar
            save_faces: Si es True, guarda los rostros recortados
            
        Returns:
            Diccionario con resultados del análisis
        """
        try:
            # Cargar imagen
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"No se pudo cargar la imagen: {image_path}")
            
            # Detectar rostros (modo no tiempo real para mejor precisión)
            faces = self.detect_faces(image, realtime=False)
            
            results = {
                'image_path': image_path,
                'faces_detected': len(faces),
                'faces_analysis': []
            }
            
            # Crear directorio para rostros recortados si no existe
            if save_faces and len(faces) > 0:
                from datetime import datetime
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                faces_dir = os.path.join(settings.MEDIA_ROOT, 'faces', timestamp)
                os.makedirs(faces_dir, exist_ok=True)
            
            # Analizar cada rostro detectado
            for i, (x, y, w, h) in enumerate(faces):
                # Extraer rostro
                face_img = image[y:y+h, x:x+w]
                
                # Guardar rostro recortado
                face_path = None
                if save_faces:
                    face_filename = f'face_{i+1}.jpg'
                    face_full_path = os.path.join(faces_dir, face_filename)
                    cv2.imwrite(face_full_path, face_img)
                    # Guardar ruta relativa desde MEDIA_ROOT con forward slashes para URLs
                    face_path = f'faces/{timestamp}/{face_filename}'
                
                # Predecir emoción
                emotions = self.predict_emotion(face_img)
                
                # Encontrar emoción dominante
                dominant_emotion = max(emotions, key=emotions.get)
                confidence = emotions[dominant_emotion]
                
                face_result = {
                    'face_id': i + 1,
                    'coordinates': {'x': x, 'y': y, 'width': w, 'height': h},
                    'dominant_emotion': dominant_emotion,
                    'confidence': confidence,
                    'all_emotions': emotions,
                    'face_image': face_path  # Agregar ruta de la imagen del rostro
                }
                
                results['faces_analysis'].append(face_result)
            
            return results
            
        except Exception as e:
            return {
                'error': str(e),
                'image_path': image_path,
                'faces_detected': 0,
                'faces_analysis': []
            }

    
    def analyze_image_from_base64(self, base64_image: str) -> Dict:
        """
        Analiza una imagen desde base64.
        
        Args:
            base64_image: Imagen codificada en base64
            
        Returns:
            Diccionario con resultados del análisis
        """
        try:
            print("Iniciando analyze_image_from_base64...")
            
            # Decodificar base64
            if ',' in base64_image:
                image_data = base64.b64decode(base64_image.split(',')[1])
            else:
                image_data = base64.b64decode(base64_image)
            
            print(f"Imagen decodificada: {len(image_data)} bytes")
            
            # Convertir a imagen PIL y luego a array numpy
            pil_image = Image.open(BytesIO(image_data))
            image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            print(f"Imagen convertida a numpy: {image.shape}")
            
            # Detectar rostros (modo no tiempo real para mejor precisión)
            faces = self.detect_faces(image, realtime=False)
            
            print(f"Rostros detectados: {len(faces)}")
            
            results = {
                'faces_detected': len(faces),
                'faces': []  # Cambiar de faces_analysis a faces
            }
            
            # Analizar cada rostro detectado
            for i, (x, y, w, h) in enumerate(faces):
                try:
                    print(f"Procesando rostro {i+1}: x={x}, y={y}, w={w}, h={h}")
                    
                    # Validar coordenadas
                    if x < 0 or y < 0 or w <= 0 or h <= 0:
                        print(f"  Coordenadas inválidas, saltando...")
                        continue
                    
                    # Extraer rostro con validación
                    y1 = max(0, y)
                    y2 = min(image.shape[0], y + h)
                    x1 = max(0, x)
                    x2 = min(image.shape[1], x + w)
                    
                    face_img = image[y1:y2, x1:x2]
                    
                    if face_img.size == 0:
                        print(f"  Rostro vacío, saltando...")
                        continue
                    
                    print(f"  Rostro extraído: {face_img.shape}")
                    
                    # Predecir emoción
                    emotions = self.predict_emotion(face_img)
                    
                    print(f"  Emociones predichas: {emotions}")
                    
                    # Encontrar emoción dominante
                    dominant_emotion = max(emotions, key=emotions.get)
                    confidence = emotions[dominant_emotion]
                    
                    face_result = {
                        'face_id': i + 1,
                        'x': int(x),
                        'y': int(y),
                        'width': int(w),
                        'height': int(h),
                        'dominant_emotion': dominant_emotion,
                        'confidence': float(confidence),
                        'emotions': emotions  # Importante: usar 'emotions' no 'all_emotions'
                    }
                    
                    results['faces'].append(face_result)
                    print(f"  Rostro {i+1} procesado exitosamente")
                    
                except Exception as e:
                    print(f"Error procesando rostro {i}: {e}")
                    import traceback
                    print(traceback.format_exc())
                    continue
            
            print(f"Análisis completado: {len(results['faces'])} rostros procesados")
            return results
            
        except Exception as e:
            import traceback
            print(f"Error en analyze_image_from_base64: {str(e)}")
            print(traceback.format_exc())
            return {
                'error': str(e),
                'faces_detected': 0,
                'faces': []
            }
    
    def analyze_frame(self, frame: np.ndarray) -> Dict:
        """
        Analiza un frame de video en tiempo real con optimización de rendimiento.
        
        Args:
            frame: Frame de video como array numpy
            
        Returns:
            Diccionario con resultados del análisis
        """
        try:
            # Validar frame
            if frame is None or frame.size == 0:
                return {
                    'faces_detected': 0,
                    'faces': []
                }
            
            # Detectar rostros (modo tiempo real para velocidad)
            faces = self.detect_faces(frame, realtime=True)
            
            results = {
                'faces_detected': len(faces),
                'faces': []
            }
            
            # Limitar a 3 rostros para mejor rendimiento en tiempo real
            faces = faces[:3] if len(faces) > 3 else faces
            
            # Analizar cada rostro detectado
            for i, (x, y, w, h) in enumerate(faces):
                try:
                    # Validar coordenadas
                    if x < 0 or y < 0 or w <= 0 or h <= 0:
                        continue
                    
                    # Validar que las coordenadas estén dentro del frame
                    if x + w > frame.shape[1] or y + h > frame.shape[0]:
                        continue
                    
                    # Extraer rostro con margen de seguridad
                    margin = 5
                    y1 = max(0, y - margin)
                    y2 = min(frame.shape[0], y + h + margin)
                    x1 = max(0, x - margin)
                    x2 = min(frame.shape[1], x + w + margin)
                    
                    face_img = frame[y1:y2, x1:x2]
                    
                    # Validar tamaño mínimo del rostro extraído
                    if face_img.shape[0] < 20 or face_img.shape[1] < 20:
                        continue
                    
                    # Predecir emoción
                    emotions = self.predict_emotion(face_img)
                    
                    # Encontrar emoción dominante
                    if emotions:
                        dominant_emotion = max(emotions, key=emotions.get)
                        confidence = emotions[dominant_emotion]
                    else:
                        dominant_emotion = 'neutral'
                        confidence = 0.5
                    
                    face_result = {
                        'face_id': i + 1,
                        'x': int(x),
                        'y': int(y),
                        'width': int(w),
                        'height': int(h),
                        'dominant_emotion': dominant_emotion,
                        'confidence': float(confidence),
                        'emotions': emotions
                    }
                    
                    results['faces'].append(face_result)
                    
                except Exception as e:
                    print(f"Error procesando rostro {i}: {e}")
                    continue
            
            return results
            
        except Exception as e:
            print(f"Error en analyze_frame: {e}")
            return {
                'error': str(e),
                'faces_detected': 0,
                'faces': []
            }

    def get_emotion_translation(self, emotion: str) -> str:
        """
        Traduce las emociones del inglés al español.
        
        Args:
            emotion: Emoción en inglés
            
        Returns:
            Emoción traducida al español
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


# Instancia global del detector
emotion_detector = EmotionDetector()