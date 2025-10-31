from django.views.generic import CreateView, View
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction

from apps.security.forms.signup_form import SignupForm
from apps.security.models import User
from apps.security.utils.setup_groups import setup_client_group

class SignupView(View):
    """Vista para registro de nuevos usuarios"""
    
    def dispatch(self, request, *args, **kwargs):
        # Redirigir a dashboard si el usuario ya está autenticado
        if request.user.is_authenticated:
            return redirect('emotions:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        """Muestra el formulario de registro"""
        form = SignupForm()
        return render(request, 'registration/signup.html', {
            'form': form,
        })
    
    def post(self, request):
        """Procesa el formulario de registro"""
        form = SignupForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Guarda el usuario y lo autentica
            user = form.save()
            
            # Usar una transacción para garantizar la integridad de los datos
            with transaction.atomic():
                # Configurar y obtener el grupo "Clientes"
                clients_group = setup_client_group()
                
                # Asignar el usuario al grupo
                user.groups.add(clients_group)
                user.save()
                
            
            # Autenticar al usuario
            login(request, user)
            
            # Establecer el grupo como activo en la sesión
            from ..components.group_session import UserGroupSession
            group_session = UserGroupSession(request)
            group_session.set_initial_group_session()
            
            # Mostrar mensaje de bienvenida en el dashboard
            request.session['show_welcome'] = True
            return redirect('emotions:dashboard')
        
        # Si el formulario no es válido, volvemos a mostrarlo con errores
        return render(request, 'registration/signup.html', {
            'form': form,
            'error': "Error al registrar usuario. Por favor, verifique los datos."
        })
