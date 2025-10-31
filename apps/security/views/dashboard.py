from django.views.generic import TemplateView
from django.contrib import messages
from django.urls import reverse
from apps.security.components.menu_module import MenuModule
from apps.security.components.mixin_crud import PermissionMixin
from apps.security.components.menu_module import MenuModule
from apps.security.components.group_session import UserGroupSession
from apps.security.components.group_permission import GroupPermission
from apps.security.models import GroupModulePermission

class DashboardView(TemplateView):
    template_name = "layouts/dashboard.html"

    #Enviar contexto al template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user

        # Mostrar mensaje de bienvenida solo si viene de inicio de sesión
        if self.request.session.pop('show_welcome', False):
            messages.success(self.request, f"¡Bienvenido, {user.get_full_name() or user.username}!, disfruta del sistema.")

        return context
    
