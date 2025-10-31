from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import json
from django.contrib.auth.models import Group
from apps.security.views.dashboard import DashboardView

#Se implemento esto con ayuda de la IA para manejar el cambio de grupo activo del usuario por errores de sesión

@require_POST
def cambiar_grupo(request):
    """
    Vista para cambiar el grupo activo del usuario en la sesión.
    Acepta tanto datos JSON como datos de formulario estándar.
    """
    try:
        # Determinar si los datos vienen como JSON o como POST normal
        if request.content_type and 'application/json' in request.content_type:
            data = json.loads(request.body)
            group_id = data.get('group_id') or data.get('gpid')
        else:
            # Datos de formulario normal
            group_id = request.POST.get('group_id') or request.POST.get('gpid')
        
        if not group_id:
            from django.contrib import messages
            messages.error(request, "No se proporcionó un ID de grupo")
            return redirect('security:dashboard')
            
        # Verificar que el grupo exista
        try:
            group = Group.objects.get(pk=group_id)
        except Group.DoesNotExist:
            from django.contrib import messages
            messages.error(request, "El grupo seleccionado no existe")
            return redirect('security:dashboard')
        
        # Verificar que el usuario pertenezca al grupo
        if group in request.user.groups.all():
            # Guardar el grupo en la sesión
            request.session['group_id'] = group.id
            
            # Si es una solicitud AJAX, devolver JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': f'Grupo cambiado a {group.name}'})
            
            # Si es una solicitud normal, redirigir al dashboard con mensaje de éxito
            from django.shortcuts import redirect
            from django.contrib import messages
            messages.success(request, f'Has cambiado al grupo: {group.name}')
            return redirect('security:dashboard')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'No perteneces a este grupo'}, status=403)
            
            from django.contrib import messages
            messages.error(request, 'No perteneces al grupo seleccionado')
            return redirect('security:dashboard')
    
    except Group.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Grupo no encontrado'}, status=404)
        
        from django.contrib import messages
        from django.shortcuts import redirect
        messages.error(request, 'El grupo seleccionado no existe')
        return redirect('security:dashboard')
        
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        
        from django.contrib import messages
        from django.shortcuts import redirect
        messages.error(request, f'Error al cambiar de grupo: {str(e)}')
        return redirect('security:dashboard')
