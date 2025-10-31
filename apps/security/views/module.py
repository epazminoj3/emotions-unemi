from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from django.shortcuts import redirect
from apps.security.models import Module
from apps.security.forms.module_form import ModuleForm

from apps.security.components.mixin_crud import (
    ListViewMixin, 
    CreateViewMixin,
    UpdateViewMixin,
    DetailViewMixin,
    DeleteViewMixin,
    PermissionMixin
)

from django.views.generic import (
    ListView, 
    CreateView,
    UpdateView,
    DeleteView,
    DetailView
)

class ModuleListView(PermissionMixin, ListViewMixin, ListView):
    template_name = 'modulo/list.html'
    model = Module
    context_object_name = 'modules'
    permission_required = 'view_module'
    paginate_by = 10

    def get_queryset(self):
        q = self.request.GET.get('q')
        queryset = self.model.objects.select_related('menu').all()
        if q:
            self.query.add(Q(name__icontains=q) | Q(url__icontains=q), Q.AND)
        return queryset.filter(self.query).order_by('menu', 'order', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb_list'] = [
            {'label': 'Inicio', 'url': '/security/'},
            {'label': 'Lista de Módulos', 'url': ''}
        ]
        context['create'] = reverse_lazy('security:module_create')
        context['title'] = 'Gestión de Módulos'
        context['total_modules'] = Module.objects.count()
        return context

class ModuleCreateView(PermissionMixin, CreateViewMixin, CreateView):
    model = Module
    template_name = 'modulo/form.html'
    form_class = ModuleForm
    success_url = reverse_lazy('security:module_list')
    permission_required = 'add_module'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Módulo'
        context['submit_text'] = 'Guardar Módulo'
        context['breadcrumb_list'] = [
            {'label': 'Inicio', 'url': '/security/'},
            {'label': 'Lista de Módulos', 'url': '/security/modules/'},
            {'label': 'Creando Módulo', 'url': ''}
        ]
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Módulo '{self.object.name}' creado con éxito.")
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.error(self.request, "Error en el formulario.")
        return response

class ModuleUpdateView(PermissionMixin, UpdateViewMixin, UpdateView):
    model = Module
    template_name = 'modulo/form.html'
    form_class = ModuleForm
    success_url = reverse_lazy('security:module_list')
    permission_required = 'change_module'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Actualizar Módulo'
        context['submit_text'] = 'Actualizar Módulo'
        context['breadcrumb_list'] = [
            {'label': 'Inicio', 'url': '/security/'},
            {'label': 'Lista de Módulos', 'url': '/security/modules/'},
            {'label': f'Actualización/{self.object.name}', 'url': ''}
        ]
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Módulo '{self.object.name}' actualizado con éxito.")
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.error(self.request, "Error en el formulario.")
        return response

class ModuleDeleteView(PermissionMixin, DeleteViewMixin, DeleteView):
    model = Module
    success_url = reverse_lazy('security:module_list')
    permission_required = 'delete_module'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Eliminar Módulo: {self.object.name}'
        return context

    def post(self, request, *args, **kwargs):
        module = self.get_object()
        module_name = module.name
        response = super().post(request, *args, **kwargs)
        messages.success(request, f"Módulo '{module_name}' eliminado con éxito.")
        return response

    def delete(self, request, *args, **kwargs):
        module = self.get_object()
        module_name = module.name
        try:
            module.delete()
            messages.success(request, f"Módulo '{module_name}' eliminado con éxito.")
            return redirect(self.success_url)
        except Exception as e:
            messages.error(request, f"Error al eliminar el módulo: {str(e)}")
            return redirect(self.success_url)

class ModuleDetailView(PermissionMixin, DetailViewMixin, DetailView):
    model = Module
    template_name = 'modulo/detail.html'
    context_object_name = 'current_module'
    permission_required = 'view_module'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb_list'] = [
            {'label': 'Inicio', 'url': '/security/'},
            {'label': 'Lista de Módulos', 'url': '/security/modules/'},
            {'label': f'Detalle/{self.object.name}', 'url': ''}
        ]
        return context