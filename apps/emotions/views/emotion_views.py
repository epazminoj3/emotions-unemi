"""
Vistas para la aplicación de detección de emociones.
"""
import os
import time
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.db.models import Q
from django.conf import settings
import base64
from io import BytesIO
from PIL import Image

from apps.emotions.models import EmotionAnalysis, EmotionStatistics
from apps.emotions.forms import EmotionAnalysisForm, ImageUploadForm, CameraAnalysisForm
from apps.emotions.services.emotion_detector import emotion_detector


@login_required
def emotion_dashboard(request):
    """
    Dashboard principal de análisis de emociones.
    """
    user = request.user
    
    # Obtener estadísticas del usuario
    stats, created = EmotionStatistics.objects.get_or_create(user=user)
    if created or stats.total_analyses == 0:
        stats.update_statistics()
    
    # Obtener análisis recientes
    recent_analyses = EmotionAnalysis.objects.filter(user=user)[:5]
    
    # Preparar datos para gráficos
    emotion_distribution = stats.get_emotion_distribution_dict()
    
    context = {
        'stats': stats,
        'recent_analyses': recent_analyses,
        'emotion_distribution': emotion_distribution,
        'emotion_distribution_json': json.dumps(emotion_distribution),
    }
    
    return render(request, 'emotions/dashboard.html', context)


@login_required
def upload_analysis(request):
    """
    Vista para subir y analizar imágenes.
    """
    if request.method == 'POST':
        form = EmotionAnalysisForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                start_time = time.time()
                
                # Crear instancia pero no guardar aún
                analysis = form.save(commit=False)
                analysis.user = request.user
                
                # Guardar la imagen primero
                analysis.save()
                
                # Realizar análisis de emociones
                image_path = analysis.image.path
                results = emotion_detector.analyze_image(image_path)
                
                # Calcular confianza promedio y emoción dominante
                faces_analysis = results.get('faces_analysis', [])
                if faces_analysis:
                    # Calcular confianza promedio
                    total_confidence = sum(face['confidence'] * 100 for face in faces_analysis)
                    analysis.average_confidence = total_confidence / len(faces_analysis)
                    
                    # Calcular emoción dominante
                    emotion_counts = {}
                    for face in faces_analysis:
                        emotion = face.get('dominant_emotion')
                        if emotion:
                            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
                    
                    if emotion_counts:
                        analysis.dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0]
                
                # Guardar resultados
                analysis.analysis_results = results
                analysis.faces_detected = results.get('faces_detected', 0)
                analysis.processing_time = time.time() - start_time
                analysis.save()
                
                # Actualizar estadísticas del usuario
                stats, created = EmotionStatistics.objects.get_or_create(user=request.user)
                stats.update_statistics()
                
                if results.get('error'):
                    messages.error(request, f"Error en el análisis: {results['error']}")
                elif analysis.faces_detected == 0:
                    messages.warning(request, "No se detectaron rostros en la imagen.")
                else:
                    messages.success(request, f"Análisis completado. Se detectaron {analysis.faces_detected} rostro(s).")
                
                return redirect('emotions:analysis_detail', pk=analysis.pk)
                
            except Exception as e:
                messages.error(request, f"Error durante el procesamiento: {str(e)}")
                # Eliminar el análisis si falló
                if 'analysis' in locals() and analysis.pk:
                    analysis.delete()
    else:
        form = EmotionAnalysisForm()
    
    context = {
        'form': form,
        'title': 'Subir Imagen para Análisis'
    }
    return render(request, 'emotions/upload.html', context)


@login_required
def analysis_detail(request, pk):
    """
    Vista de detalle de un análisis de emociones.
    """
    analysis = get_object_or_404(EmotionAnalysis, pk=pk, user=request.user)
    
    # Preparar datos para visualización
    faces_summary = analysis.get_faces_summary()
    emotion_distribution = analysis.get_emotion_distribution()
    
    context = {
        'analysis': analysis,
        'faces_summary': faces_summary,
        'emotion_distribution': emotion_distribution,
        'emotion_distribution_json': json.dumps(emotion_distribution),
    }
    
    return render(request, 'emotions/detail.html', context)


@login_required
def analysis_list(request):
    """
    Lista de análisis de emociones del usuario.
    """
    analyses = EmotionAnalysis.objects.filter(user=request.user)
    
    # Filtros
    emotion_filter = request.GET.get('emotion')
    date_filter = request.GET.get('date')
    
    if emotion_filter and emotion_filter != 'all':
        analyses = analyses.filter(dominant_emotion=emotion_filter)
    
    if date_filter:
        from django.utils import timezone
        from datetime import timedelta
        
        if date_filter == 'today':
            analyses = analyses.filter(created_at__date=timezone.now().date())
        elif date_filter == 'week':
            week_ago = timezone.now() - timedelta(days=7)
            analyses = analyses.filter(created_at__gte=week_ago)
        elif date_filter == 'month':
            month_ago = timezone.now() - timedelta(days=30)
            analyses = analyses.filter(created_at__gte=month_ago)
    
    # Búsqueda
    search_query = request.GET.get('search')
    if search_query:
        analyses = analyses.filter(
            Q(notes__icontains=search_query) |
            Q(dominant_emotion__icontains=search_query)
        )
    
    # Paginación
    paginator = Paginator(analyses, 12)  # 12 análisis por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Opciones para filtros
    emotion_options = [
        ('all', 'Todas las emociones'),
        ('neutral', 'Neutral'),
        ('happiness', 'Felicidad'),
        ('surprise', 'Sorpresa'),
        ('sadness', 'Tristeza'),
        ('anger', 'Ira'),
        ('disgust', 'Disgusto'),
        ('fear', 'Miedo'),
        ('contempt', 'Desprecio'),
    ]
    
    context = {
        'page_obj': page_obj,
        'emotion_options': emotion_options,
        'current_emotion': emotion_filter or 'all',
        'current_date': date_filter or 'all',
        'search_query': search_query or '',
    }
    
    return render(request, 'emotions/list.html', context)


@login_required
def quick_analysis(request):
    """
    Vista para análisis rápido sin guardar en base de datos.
    """
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Guardar imagen temporalmente
                image = form.cleaned_data['image']
                
                # Crear archivo temporal
                import tempfile
                import time
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                    for chunk in image.chunks():
                        temp_file.write(chunk)
                    temp_path = temp_file.name
                
                # Realizar análisis (sin guardar rostros en análisis rápido)
                start_time = time.time()
                results = emotion_detector.analyze_image(temp_path, save_faces=False)
                processing_time = time.time() - start_time
                
                # Limpiar archivo temporal
                os.unlink(temp_path)
                
                # Calcular confianza promedio
                faces_list = results.get('faces_analysis', [])
                avg_confidence = 0
                if faces_list:
                    avg_confidence = sum(f.get('confidence', 0) for f in faces_list) / len(faces_list)
                
                # Normalizar formato de cada rostro para el frontend
                normalized_faces = []
                for face in faces_list:
                    normalized_face = {
                        'face_id': face.get('face_id'),
                        'coordinates': face.get('coordinates'),
                        'dominant_emotion': face.get('dominant_emotion'),
                        'confidence': face.get('confidence'),
                        'emotions': face.get('all_emotions', {})  # Cambiar all_emotions a emotions
                    }
                    normalized_faces.append(normalized_face)
                
                # Normalizar respuesta para el frontend
                response_data = {
                    'faces_detected': results.get('faces_detected', 0),
                    'faces': normalized_faces,  # Usar lista normalizada
                    'processing_time': processing_time,
                    'average_confidence': avg_confidence
                }
                
                # Devolver JSON response
                return JsonResponse({
                    'success': True,
                    'analysis': response_data
                })
                
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Formulario inválido'
            })
    else:
        form = ImageUploadForm()
    
    context = {
        'form': form,
        'title': 'Análisis Rápido de Emociones'
    }
    return render(request, 'emotions/quick_analysis.html', context)


@login_required
def camera_analysis(request):
    """
    Vista para análisis desde cámara web.
    """
    if request.method == 'POST':
        try:
            # Manejar tanto JSON como FormData
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                image_data = data.get('image_data')
                save_analysis = data.get('save_analysis', False)
                notes = data.get('notes', '')
            else:
                # FormData desde el formulario
                image_data = request.POST.get('image_data')
                save_analysis = request.POST.get('save_analysis') == 'true'
                notes = request.POST.get('notes', '')
            
            if not image_data:
                return JsonResponse({
                    'success': False,
                    'error': 'No se proporcionó imagen'
                })
            
            # Realizar análisis
            results = emotion_detector.analyze_image_from_base64(image_data)
            
            if save_analysis and not results.get('error'):
                # Guardar en base de datos
                # Convertir base64 a archivo
                try:
                    format, imgstr = image_data.split(';base64,')
                    ext = format.split('/')[-1]
                    
                    import uuid
                    filename = f"camera_capture_{uuid.uuid4().hex}.{ext}"
                    
                    analysis = EmotionAnalysis(
                        user=request.user,
                        notes=notes,
                        analysis_results=results,
                        faces_detected=results.get('faces_detected', 0),
                        average_confidence=results.get('average_confidence', 0.0),
                        processing_time=results.get('processing_time', 0.0)
                    )
                    
                    # Guardar imagen desde base64
                    image_file = ContentFile(
                        base64.b64decode(imgstr),
                        name=filename
                    )
                    analysis.image.save(filename, image_file, save=False)
                    analysis.save()
                    
                    # Actualizar estadísticas
                    stats, created = EmotionStatistics.objects.get_or_create(user=request.user)
                    stats.update_statistics()
                    
                    return JsonResponse({
                        'success': True,
                        'analysis': results,
                        'saved': True,
                        'analysis_id': analysis.pk,
                        'redirect_url': f'/emotions/analysis/{analysis.pk}/'
                    })
                except Exception as e:
                    return JsonResponse({
                        'success': True,
                        'analysis': results,
                        'saved': False,
                        'error': f'Error guardando: {str(e)}'
                    })
            else:
                return JsonResponse({
                    'success': True,
                    'analysis': results,
                    'saved': False
                })
                    
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    else:
        form = CameraAnalysisForm()
    
    context = {
        'form': form,
        'title': 'Análisis desde Cámara'
    }
    return render(request, 'emotions/camera.html', context)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def api_analyze_base64(request):
    """
    API para análisis de imágenes en base64 (AJAX).
    """
    try:
        data = json.loads(request.body)
        image_data = data.get('image_data')
        
        if not image_data:
            return JsonResponse({
                'success': False,
                'error': 'No se proporcionaron datos de imagen'
            })
        
        # Realizar análisis
        start_time = time.time()
        results = emotion_detector.analyze_image_from_base64(image_data)
        processing_time = time.time() - start_time
        
        # Agregar tiempo de procesamiento
        results['processing_time'] = processing_time
        
        return JsonResponse({
            'success': True,
            'analysis': results  # Cambiar de 'results' a 'analysis'
        })
        
    except Exception as e:
        import traceback
        print(f"Error en api_analyze_base64: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def delete_analysis(request, pk):
    """
    Vista para eliminar un análisis.
    """
    analysis = get_object_or_404(EmotionAnalysis, pk=pk, user=request.user)
    
    if request.method == 'POST':
        # Eliminar archivo de imagen
        if analysis.image:
            try:
                default_storage.delete(analysis.image.name)
            except:
                pass  # Si hay error al eliminar el archivo, continuar
        
        analysis.delete()
        
        messages.success(request, 'Análisis eliminado correctamente.')
        return redirect('emotions:analysis_list')
    
    return render(request, 'emotions/delete_analysis.html', {
        'analysis': analysis,
        'title': 'Eliminar Análisis'
    })

@login_required
def user_statistics(request):
    """
    Vista de estadísticas detalladas del usuario.
    """
    stats, created = EmotionStatistics.objects.get_or_create(user=request.user)
    if created or stats.total_analyses == 0:
        stats.update_statistics()
    
    # Obtener análisis para gráficos adicionales
    analyses = EmotionAnalysis.objects.filter(user=request.user).order_by('-created_at')
    
    # Datos para gráfico de tendencias (últimos 30 días)
    from django.utils import timezone
    from datetime import timedelta
    from collections import defaultdict
    
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_analyses = analyses.filter(created_at__gte=thirty_days_ago)
    
    # Agrupar por día
    daily_emotions = defaultdict(lambda: defaultdict(int))
    for analysis in recent_analyses:
        date_str = analysis.created_at.strftime('%Y-%m-%d')
        if analysis.dominant_emotion:
            emotion_translated = analysis.get_emotion_translation(analysis.dominant_emotion)
            daily_emotions[date_str][emotion_translated] += 1
    
    # Preparar datos para Chart.js
    chart_data = {
        'labels': list(daily_emotions.keys())[-14:],  # Últimos 14 días
        'datasets': []
    }
    
    emotion_colors = {
        'Felicidad': '#10B981',
        'Tristeza': '#3B82F6',
        'Ira': '#EF4444',
        'Sorpresa': '#F59E0B',
        'Miedo': '#8B5CF6',
        'Disgusto': '#84CC16',
        'Desprecio': '#F97316',
        'Neutral': '#6B7280'
    }
    
    for emotion, color in emotion_colors.items():
        data = []
        for date in chart_data['labels']:
            data.append(daily_emotions[date].get(emotion, 0))
        
        if sum(data) > 0:  # Solo incluir emociones que tienen datos
            chart_data['datasets'].append({
                'label': emotion,
                'data': data,
                'borderColor': color,
                'backgroundColor': color + '20',
                'tension': 0.4
            })
    
    # Preparar distribución de emociones con nombre y porcentaje
    emotion_dist = stats.get_emotion_distribution_dict()
    emotion_distribution_formatted = {}
    
    # Mapeo inverso de nombres traducidos a nombres en inglés
    emotion_mapping = {
        'Neutral': 'neutral',
        'Felicidad': 'happiness',
        'Sorpresa': 'surprise',
        'Tristeza': 'sadness',
        'Ira': 'anger',
        'Disgusto': 'disgust',
        'Miedo': 'fear',
        'Desprecio': 'contempt'
    }
    
    # Calcular conteos reales
    emotion_counts = {
        'Neutral': stats.neutral_count,
        'Felicidad': stats.happiness_count,
        'Sorpresa': stats.surprise_count,
        'Tristeza': stats.sadness_count,
        'Ira': stats.anger_count,
        'Disgusto': stats.disgust_count,
        'Miedo': stats.fear_count,
        'Desprecio': stats.contempt_count
    }
    
    for emotion_es, emotion_en in emotion_mapping.items():
        if emotion_counts[emotion_es] > 0:
            emotion_distribution_formatted[emotion_es.lower()] = {
                'name': emotion_es,
                'count': emotion_counts[emotion_es],
                'percentage': emotion_dist.get(emotion_es, 0)
            }
    
    # Calcular estadísticas de tiempo
    seven_days_ago = timezone.now() - timedelta(days=7)
    
    context = {
        'stats': stats,
        'total_analyses': analyses.count(),
        'emotion_distribution': emotion_distribution_formatted,
        'emotion_distribution_json': json.dumps(emotion_dist),
        'chart_data': json.dumps(chart_data),
        'last_7_days': analyses.filter(created_at__gte=seven_days_ago).count(),
        'last_30_days': recent_analyses.count(),
        'this_month': analyses.filter(created_at__month=timezone.now().month, created_at__year=timezone.now().year).count(),
    }
    
    return render(request, 'emotions/statistics.html', context)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def api_save_camera_analysis(request):
    """
    API para guardar análisis de cámara en el historial.
    Recibe imagen base64 y datos del análisis.
    """
    try:
        data = json.loads(request.body)
        
        # Obtener datos
        image_data = data.get('image_data')
        analysis_results = data.get('analysis_results')
        notes = data.get('notes', '')
        
        if not image_data or not analysis_results:
            return JsonResponse({
                'success': False,
                'error': 'Faltan datos requeridos'
            }, status=400)
        
        # Decodificar imagen base64
        if image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]
        
        image_binary = base64.b64decode(image_data)
        image = Image.open(BytesIO(image_binary))
        
        # Crear análisis
        # Calcular confianza promedio correctamente (convertir a porcentaje si es necesario)
        avg_confidence = analysis_results.get('average_confidence', 0)
        # Si la confianza es menor a 1, está en formato decimal (0-1), convertir a porcentaje
        if avg_confidence > 0 and avg_confidence < 1:
            avg_confidence = avg_confidence * 100
        
        analysis = EmotionAnalysis.objects.create(
            user=request.user,
            notes=notes,
            faces_detected=analysis_results.get('faces_detected', 0),
            analysis_results=analysis_results,
            processing_time=analysis_results.get('processing_time', 0),
            average_confidence=avg_confidence
        )
        
        # Guardar imagen
        buffer = BytesIO()
        image.save(buffer, format='JPEG', quality=90)
        buffer.seek(0)
        
        filename = f'camera_analysis_{analysis.id}_{int(time.time())}.jpg'
        analysis.image.save(filename, ContentFile(buffer.read()), save=False)
        
        # Calcular emoción dominante
        if analysis_results.get('faces') and len(analysis_results['faces']) > 0:
            emotions_count = {}
            for face in analysis_results['faces']:
                if 'emotions' in face:
                    dominant = max(face['emotions'].items(), key=lambda x: x[1])
                    emotions_count[dominant[0]] = emotions_count.get(dominant[0], 0) + 1
            
            if emotions_count:
                analysis.dominant_emotion = max(emotions_count.items(), key=lambda x: x[1])[0]
        
        analysis.save()
        
        # Actualizar estadísticas
        stats, created = EmotionStatistics.objects.get_or_create(user=request.user)
        stats.update_statistics()
        
        return JsonResponse({
            'success': True,
            'analysis_id': analysis.pk,
            'redirect_url': f'/emotions/analysis/{analysis.pk}/',
            'message': 'Análisis guardado exitosamente'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error guardando análisis: {str(e)}'
        }, status=500)