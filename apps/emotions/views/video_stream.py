"""
Vista para transmisión de video en tiempo real con detección de emociones.
"""
import cv2
import json
import threading
import time
from django.http import StreamingHttpResponse, JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from apps.emotions.services.emotion_detector import emotion_detector


class VideoCamera:
    """
    Clase para manejar la cámara y el streaming de video con manejo thread-safe.
    """
    def __init__(self, camera_id=0):
        self.camera_id = camera_id
        self.video = None
        self.lock = threading.Lock()
        self.last_frame = None
        self.last_frame_time = 0
        self.frame_skip_threshold = 0.033  # ~30 FPS
        
        # Variables para detección
        self.detect_emotions = False
        self.last_detection_time = 0
        self.detection_interval = 0.5  # Detectar cada 0.5 segundos
        self.current_results = {}
        
        # Estado de inicialización
        self.is_initialized = False
        self.init_camera(camera_id)
        
    def init_camera(self, camera_id=0):
        """
        Inicializa la cámara con el ID especificado con mejoras para evitar errores.
        """
        with self.lock:
            try:
                # Liberar cámara anterior completamente
                if self.video is not None:
                    self.video.release()
                    time.sleep(0.5)  # Dar tiempo para liberar recursos
                    self.video = None
                
                # Configurar nuevo ID
                self.camera_id = camera_id
                
                # Inicializar nueva cámara con backend específico de Windows
                if camera_id == '' or camera_id is None:
                    camera_id = 0
                else:
                    try:
                        camera_id = int(camera_id)
                    except:
                        camera_id = 0
                
                # Usar backend DSHOW (DirectShow) en Windows para mejor rendimiento
                self.video = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
                
                if not self.video.isOpened():
                    print(f"Error: No se pudo abrir la cámara {camera_id}")
                    self.is_initialized = False
                    return False
                
                # Configurar propiedades de la cámara
                self.video.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.video.set(cv2.CAP_PROP_FPS, 30)
                self.video.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Buffer mínimo para reducir lag
                
                # Verificar que se inicializó correctamente
                ret, frame = self.video.read()
                if not ret or frame is None:
                    print(f"Error: No se pudo leer de la cámara {camera_id}")
                    self.video.release()
                    self.video = None
                    self.is_initialized = False
                    return False
                
                self.last_frame = frame
                self.last_frame_time = time.time()
                self.is_initialized = True
                
                print(f"✓ Cámara {camera_id} inicializada correctamente")
                return True
                
            except Exception as e:
                print(f"✗ Error inicializando cámara {camera_id}: {e}")
                if self.video is not None:
                    self.video.release()
                    self.video = None
                self.is_initialized = False
                return False
    
    def change_camera(self, camera_id):
        """
        Cambia a una cámara diferente de forma segura.
        """
        # Detener detección antes de cambiar
        self.detect_emotions = False
        time.sleep(0.1)
        
        # Inicializar nueva cámara
        success = self.init_camera(camera_id)
        
        if success:
            print(f"✓ Cámara cambiada exitosamente a ID {camera_id}")
        else:
            print(f"✗ Fallo al cambiar a cámara ID {camera_id}")
        
        return success
        
    def __del__(self):
        """Destructor para liberar recursos."""
        self.cleanup()
    
    def cleanup(self):
        """Limpia y libera recursos de la cámara."""
        with self.lock:
            if self.video is not None:
                try:
                    self.video.release()
                    print("✓ Cámara liberada correctamente")
                except Exception as e:
                    print(f"Error liberando cámara: {e}")
                finally:
                    self.video = None
                    self.is_initialized = False
    
    def get_frame(self):
        """
        Obtener frame de la cámara con control de flujo mejorado.
        """
        with self.lock:
            if not self.is_initialized or self.video is None or not self.video.isOpened():
                # Retornar último frame válido si existe
                if self.last_frame is not None:
                    return self._encode_frame(self.last_frame)
                return None
            
            try:
                # Limitar frecuencia de captura para evitar sobrecarga
                current_time = time.time()
                time_since_last_frame = current_time - self.last_frame_time
                
                if time_since_last_frame < self.frame_skip_threshold:
                    # Reusar último frame para mantener FPS suave
                    if self.last_frame is not None:
                        return self._encode_frame(self.last_frame)
                    return None
                
                # Leer frame con timeout implícito
                success = False
                frame = None
                
                # Intentar leer frame hasta 3 veces
                for attempt in range(3):
                    success, frame = self.video.read()
                    if success and frame is not None:
                        break
                    time.sleep(0.01)  # Pequeña pausa entre intentos
                
                if not success or frame is None:
                    # Reusar último frame válido
                    if self.last_frame is not None:
                        return self._encode_frame(self.last_frame)
                    return None
                
                # Actualizar último frame y tiempo
                self.last_frame = frame.copy()
                self.last_frame_time = current_time
                
                # Aplicar detección de emociones si está habilitada
                if self.detect_emotions:
                    frame = self._apply_detection(frame)
                
                return self._encode_frame(frame)
                
            except Exception as e:
                print(f"Error capturando frame: {e}")
                # Retornar último frame válido en caso de error
                if self.last_frame is not None:
                    return self._encode_frame(self.last_frame)
                return None
    
    def _apply_detection(self, frame):
        """
        Aplica detección de emociones al frame.
        """
        current_time = time.time()
        
        # Solo detectar cada cierto intervalo para optimizar performance
        if current_time - self.last_detection_time > self.detection_interval:
            try:
                # Realizar detección en una copia del frame
                frame_copy = frame.copy()
                results = emotion_detector.analyze_frame(frame_copy)
                self.current_results = results
                self.last_detection_time = current_time
            except Exception as e:
                print(f"Error en detección: {e}")
                self.current_results = {}
        
        # Dibujar resultados en el frame
        return self._draw_results_on_frame(frame)
    
    def _encode_frame(self, frame):
        """
        Codifica el frame a JPEG bytes.
        """
        try:
            ret, buffer = cv2.imencode('.jpg', frame, [
                cv2.IMWRITE_JPEG_QUALITY, 80,
                cv2.IMWRITE_JPEG_OPTIMIZE, 1
            ])
            if not ret or buffer is None:
                return None
            return buffer.tobytes()
        except Exception as e:
            print(f"Error codificando frame: {e}")
            return None
    
    def _draw_results_on_frame(self, frame):
        """
        Dibujar resultados de detección en el frame.
        """
        if not self.current_results or 'faces' not in self.current_results:
            return frame
        
        try:
            # Crear copia para no modificar el original
            display_frame = frame.copy()
            
            for face in self.current_results['faces']:
                # Obtener coordenadas del rostro
                x = int(face.get('x', 0))
                y = int(face.get('y', 0))
                width = int(face.get('width', 0))
                height = int(face.get('height', 0))
                
                # Validar coordenadas
                if x < 0 or y < 0 or width <= 0 or height <= 0:
                    continue
                
                # Dibujar rectángulo alrededor del rostro
                cv2.rectangle(display_frame, (x, y), (x + width, y + height), (0, 255, 0), 2)
                
                # Obtener emoción dominante
                emotions = face.get('emotions', {})
                if emotions:
                    dominant_emotion = max(emotions.items(), key=lambda x: x[1])
                    emotion_name = emotion_detector.get_emotion_translation(dominant_emotion[0])
                    confidence = dominant_emotion[1] * 100
                    
                    # Texto de la emoción
                    text = f"{emotion_name}: {confidence:.1f}%"
                    
                    # Configurar texto
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    font_scale = 0.6
                    thickness = 2
                    
                    # Calcular tamaño del texto
                    (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)
                    
                    # Asegurar que el texto no salga del frame
                    text_y = max(y - 5, text_height + 10)
                    
                    # Fondo para el texto
                    cv2.rectangle(display_frame, 
                                (x, text_y - text_height - 10), 
                                (x + text_width, text_y), 
                                (0, 255, 0), -1)
                    
                    # Texto
                    cv2.putText(display_frame, text, (x, text_y - 5), 
                              font, font_scale, (0, 0, 0), thickness)
                    
                    # Mostrar top 3 emociones en la esquina superior
                    y_offset = 30
                    for i, (emotion, score) in enumerate(sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:3]):
                        emotion_translated = emotion_detector.get_emotion_translation(emotion)
                        emotion_text = f"{emotion_translated}: {score*100:.1f}%"
                        cv2.putText(display_frame, emotion_text, (10, y_offset + i * 25), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            # Agregar información general
            info_text = f"Rostros: {len(self.current_results['faces'])}"
            cv2.putText(display_frame, info_text, (10, display_frame.shape[0] - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            return display_frame
            
        except Exception as e:
            print(f"Error dibujando resultados: {e}")
            return frame
    
    def toggle_detection(self, enable):
        """
        Activar/desactivar detección de emociones.
        """
        with self.lock:
            self.detect_emotions = enable
            if not enable:
                self.current_results = {}
                print(f"✓ Detección {'activada' if enable else 'desactivada'}")
    
    def get_current_results(self):
        """
        Obtener resultados actuales de forma thread-safe.
        """
        with self.lock:
            return self.current_results.copy() if self.current_results else {}


# Instancia global de la cámara con lock para thread safety
camera = None
camera_lock = threading.Lock()


def get_camera():
    """
    Obtener instancia de la cámara (singleton thread-safe).
    """
    global camera
    with camera_lock:
        if camera is None:
            camera = VideoCamera()
        return camera


def release_camera_instance():
    """
    Liberar instancia global de la cámara.
    """
    global camera
    with camera_lock:
        if camera is not None:
            camera.cleanup()
            camera = None


def generate_frames():
    """
    Generador de frames para streaming con manejo de errores.
    """
    camera_instance = get_camera()
    consecutive_errors = 0
    max_errors = 10
    
    while True:
        try:
            frame = camera_instance.get_frame()
            
            if frame is None:
                consecutive_errors += 1
                if consecutive_errors >= max_errors:
                    print(f"Demasiados errores consecutivos ({consecutive_errors}), reiniciando cámara...")
                    camera_instance.init_camera(camera_instance.camera_id)
                    consecutive_errors = 0
                time.sleep(0.1)  # Pausa para evitar loop muy rápido
                continue
            
            # Resetear contador de errores en frame exitoso
            consecutive_errors = 0
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
        except GeneratorExit:
            # El cliente cerró la conexión
            print("Cliente desconectado del stream")
            break
        except Exception as e:
            print(f"Error en generate_frames: {e}")
            consecutive_errors += 1
            time.sleep(0.1)
            continue


@login_required
def video_feed(request):
    """
    Vista para el streaming de video.
    """
    return StreamingHttpResponse(
        generate_frames(),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )


@login_required
def real_time_analysis(request):
    """
    Vista principal para análisis en tiempo real.
    """
    return render(request, 'emotions/real_time.html')


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def toggle_detection(request):
    """
    API para activar/desactivar detección en tiempo real.
    """
    try:
        data = json.loads(request.body)
        enable = data.get('enable', False)
        
        camera = get_camera()
        camera.toggle_detection(enable)
        
        return JsonResponse({
            'success': True,
            'detection_enabled': enable,
            'message': f"Detección {'activada' if enable else 'desactivada'} correctamente"
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_current_results(request):
    """
    API para obtener resultados actuales de detección.
    """
    try:
        camera = get_camera()
        results = camera.get_current_results()
        
        return JsonResponse({
            'success': True,
            'results': results,
            'detection_enabled': camera.detect_emotions
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def change_camera(request):
    """
    API para cambiar la cámara activa de forma segura.
    """
    try:
        data = json.loads(request.body)
        camera_id = data.get('camera_id', 0)
        
        # Validar y convertir camera_id
        if camera_id == '' or camera_id is None:
            camera_id = 0
        else:
            try:
                camera_id = int(camera_id)
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False,
                    'error': 'ID de cámara inválido'
                }, status=400)
        
        # Obtener instancia de cámara
        camera = get_camera()
        
        # Cambiar cámara
        success = camera.change_camera(camera_id)
        
        if success:
            return JsonResponse({
                'success': True,
                'camera_id': camera_id,
                'message': f'✓ Cámara cambiada exitosamente a ID {camera_id}'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'No se pudo acceder a la cámara {camera_id}. Verifica que esté conectada y no esté siendo usada por otra aplicación.',
                'camera_id': camera.camera_id  # Retornar ID de cámara actual
            }, status=400)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Datos JSON inválidos'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al cambiar cámara: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def release_camera(request):
    """
    Liberar recursos de la cámara.
    """
    try:
        release_camera_instance()
        
        return JsonResponse({
            'success': True,
            'message': 'Cámara liberada correctamente'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)