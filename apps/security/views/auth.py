from django.shortcuts import redirect, render
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django import forms
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..components.group_session import UserGroupSession
from ..models import User
from django.http import JsonResponse
from django.views import View
from django.db.models import Q

# ----------------- Cerrar Sesion -----------------
# @login_required
def signout(request):
    logout(request)
    return redirect("security:signin")

# # ----------------- Iniciar Sesion -----------------
def signin(request):
    """
    Vista para iniciar sesión.
    Acepta login con email o nombre de usuario.
    """
    data = {"title": "Login",
            "title1": "Inicio de Sesión"}
    
    if request.method == "GET":
        # Obtener mensajes de éxito de la cola de mensajes
        success_messages = messages.get_messages(request)
        return render(request, "registration/login.html", {
            "form": AuthenticationForm(),
            "success_messages": success_messages,
            **data
        })
    else:
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Primero intentamos autenticar con el nombre de usuario
            user = authenticate(request, username=username, password=password)
            
            # Si no funciona, intentamos autenticar con el email
            if user is None:
                # Verificamos si el username es un email
                try:
                    from apps.security.models import User
                    try:
                        user_obj = User.objects.get(email=username)
                        # Si encontramos el usuario, autenticamos con su nombre de usuario
                        user = authenticate(request, username=user_obj.username, password=password)
                    except User.DoesNotExist:
                        # El email no existe, seguimos con user = None
                        pass
                except ImportError:
                    # Si no podemos importar el modelo personalizado, seguimos
                    pass
            
            if user is not None:
                login(request, user)
                
                # Establecer el primer grupo como activo si no hay uno activo
                if not request.session.get('group_id') and user.groups.exists():
                    group_session = UserGroupSession(request)
                    group_session.set_initial_group_session()
                # Guardar variable en sesión para mostrar el mensaje en el dashboard
                
                request.session['show_welcome'] = True
                return redirect("emotions:dashboard")
            else:
                return render(request, "registration/login.html", {
                    "form": form,
                    "error": "El usuario o la contraseña son incorrectos",
                    **data
                })
        else:
            return render(request, "registration/login.html", {
                "form": form,
                "error": "Datos inválidos",
                **data
            })

class UserSearchApiView(View):
    def get(self, request):
        q = request.GET.get('q', '').strip()
        results = []
        if len(q) > 2:
            users = User.objects.filter(
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q) |
                Q(email__icontains=q) |
                Q(dni__icontains=q)
            )[:10]
            for user in users:
                results.append({
                    'id': user.id,
                    'name': user.get_full_name if hasattr(user, 'get_full_name') else user.username,
                    'email': user.email,
                    'cedula': getattr(user, 'dni', ''),
                })
        return JsonResponse({'results': results})