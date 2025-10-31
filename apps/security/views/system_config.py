# apps/security/views/system_config.py
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from django.shortcuts import redirect
from apps.security.models import SystemConfig
from apps.security.forms.system_config_form import SystemConfigForm

from apps.security.components.mixin_crud import (
    ListViewMixin, 
    CreateViewMixin,
    UpdateViewMixin,
    DetailViewMixin,
    PermissionMixin
)

from django.views.generic import (
    ListView, 
    CreateView,
    UpdateView,
    DetailView
)

class SystemConfigListView(PermissionMixin, ListViewMixin, ListView):
    """
    Vista para listar configuración del sistema usando el template genérico list.html
    """
    template_name = 'system_config/list.html' 
    model = SystemConfig
    context_object_name = 'configs'
    permission_required = 'view_systemconfig'
    paginate_by = 10  

    def get_queryset(self):
        q = self.request.GET.get('q')
        
        # Iniciar con la consulta base
        queryset = self.model.objects.all()
        
        # Filtrar por término de búsqueda
        if q:
            self.query.add(Q(name__icontains=q) | 
                          Q(description__icontains=q) |
                          Q(company__icontains=q), Q.AND)
        
        return queryset.filter(self.query).order_by('id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        breadcrumb_list = [
            {'label': 'Inicio', 'url': '/security/'},
            {'label': 'Configuración del Sistema', 'url': ''}
        ]

        context['breadcrumb_list'] = breadcrumb_list
        
        # URLs para las acciones
        context['create'] = reverse_lazy('security:system_config_create')
        
        # Título de la página
        context['title'] = 'Configuración del Sistema'
        
        # Estadísticas
        context['total_configs'] = SystemConfig.objects.count()
        
        return context
    
class SystemConfigCreateView(PermissionMixin, CreateViewMixin, CreateView):    
    """
    Vista para crear configuración del sistema
    """
    model = SystemConfig
    template_name = 'system_config/form.html'
    form_class = SystemConfigForm
    success_url = reverse_lazy('security:system_config_list')
    permission_required = 'add_systemconfig'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if 'form' not in context:
            context['form'] = self.get_form()

        context['title'] = 'Crear Configuración del Sistema'
        context['submit_text'] = 'Guardar Configuración'

        breadcrumb_list = [
            {'label': 'Inicio', 'url': '/security/'},
            {'label': 'Configuración del Sistema', 'url': '/security/system-config/'},
            {'label': 'Crear Configuración', 'url': ''}
        ]

        context['breadcrumb_list'] = breadcrumb_list

        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        config = self.object
        messages.success(self.request, f"Configuración '{config.name}' creada con éxito.")
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.error(self.request, f"Error en el formulario.")
        return response
        
class SystemConfigUpdateView(PermissionMixin, UpdateViewMixin, UpdateView):    
    """
    Vista para actualizar configuración del sistema
    """
    model = SystemConfig
    template_name = 'system_config/form.html'
    form_class = SystemConfigForm
    success_url = reverse_lazy('security:system_config_list')
    permission_required = 'change_systemconfig'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = self.get_form()

        context['title'] = 'Actualizar Configuración'
        context['submit_text'] = 'Actualizar Configuración'

        config = self.object

        breadcrumb_list = [
            {'label': 'Inicio', 'url': '/security/'},
            {'label': 'Configuración del Sistema', 'url': '/security/system-config/'},
            {'label': f'Actualizar/{config.name}', 'url': ''}
        ]

        context['breadcrumb_list'] = breadcrumb_list

        context['object'] = self.get_object()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        config = self.object
        messages.success(self.request, f"Configuración '{config.name}' actualizada con éxito.")
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.error(self.request, f"Error en el formulario.")
        return response

class SystemConfigDetailView(PermissionMixin, DetailViewMixin, DetailView):
    """
    Vista para ver detalles de la configuración del sistema
    """
    model = SystemConfig
    template_name = 'system_config/detail.html'
    context_object_name = 'config'
    permission_required = 'view_systemconfig'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        config = self.get_object()

        breadcrumb_list = [
            {'label': 'Inicio', 'url': '/security/'},
            {'label': 'Configuración del Sistema', 'url': '/security/system-config/'},
            {'label': f'Detalle/{config.name}', 'url': ''}
        ]

        context['breadcrumb_list'] = breadcrumb_list
        
        return context