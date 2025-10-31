from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
import json
from django.shortcuts import redirect
from apps.security.models import GroupModulePermission, Module, Group
from apps.security.forms.permission_form import GroupModulePermissionCreateForm, GroupModulePermissionEditForm

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

def module_permissions_ajax(request, module_id):
    try:
        module = Module.objects.get(pk=module_id)
        perms = module.permissions.all()
        data = [
            {'id': perm.id, 'name': perm.name, 'codename': perm.codename}
            for perm in perms
        ]
        return JsonResponse(data, safe=False)
    except Module.DoesNotExist:
        return JsonResponse([], safe=False)

class GroupModulePermissionListView(PermissionMixin, ListViewMixin, ListView):
    template_name = 'permission/list.html'
    model = GroupModulePermission
    context_object_name = 'group_module_permissions'
    permission_required = 'view_groupmodulepermission'
    paginate_by = 10

    def get_queryset(self):
        q = self.request.GET.get('q')
        queryset = self.model.objects.select_related('group', 'module').all()
        if q:
            self.query.add(Q(group__name__icontains=q) | Q(module__name__icontains=q), Q.AND)
        return queryset.filter(self.query).order_by('group', 'module')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb_list'] = [
            {'label': 'Inicio', 'url': '/security/'},
            {'label': 'Permisos por Grupo/Módulo', 'url': ''}
        ]
        context['create'] = reverse_lazy('security:group_module_permission_create')
        context['title'] = 'Permisos por Grupo y Módulo'
        context['total_permissions'] = GroupModulePermission.objects.count()
        return context

class GroupModulePermissionCreateView(PermissionMixin, CreateViewMixin, CreateView):
    model = GroupModulePermission
    form_class = GroupModulePermissionCreateForm
    template_name = 'permission/form_create.html'
    success_url = reverse_lazy('security:group_module_permission_list')
    permission_required = 'add_groupmodulepermission'

    def form_valid(self, form):
        group = form.cleaned_data['group']
        module = form.cleaned_data['module']
        # Verifica si ya existe la asignación
        if GroupModulePermission.objects.filter(group=group, module=module).exists():
            form.add_error(None, f"Ya existe una asignación para el grupo '{group.name}' y el módulo '{module.name}'. Pruebe editandolo")
            return self.form_invalid(form)
        response = super().form_valid(form)
        messages.success(self.request, "Permisos asignados correctamente.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Error al asignar permisos.")
        return super().form_invalid(form)

class GroupModulePermissionEditView(PermissionMixin, UpdateViewMixin, UpdateView):
    model = GroupModulePermission
    form_class = GroupModulePermissionEditForm
    template_name = 'permission/form_edit.html'
    success_url = reverse_lazy('security:group_module_permission_list')
    permission_required = 'change_groupmodulepermission'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar permisos de módulo para grupo'
        context['submit_text'] = 'Actualizar permisos'
        context['breadcrumb_list'] = [
            {'label': 'Inicio', 'url': '/security/'},
            {'label': 'Permisos por Grupo/Módulo', 'url': '/security/group-module-permissions/'},
            {'label': 'Editar', 'url': ''}
        ]
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Permisos actualizados correctamente.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Error al actualizar permisos.")
        return super().form_invalid(form)

class GroupModulePermissionDeleteView(PermissionMixin, DeleteViewMixin, DeleteView):
    model = GroupModulePermission
    success_url = reverse_lazy('security:group_module_permission_list')
    permission_required = 'delete_groupmodulepermission'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Eliminar Permiso de Grupo/Módulo: {self.object}'
        return context

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj_name = str(obj)
        response = super().post(request, *args, **kwargs)
        messages.success(request, f"Permiso '{obj_name}' eliminado con éxito.")
        return response

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        obj_name = str(obj)
        try:
            obj.delete()
            messages.success(request, f"Permiso '{obj_name}' eliminado con éxito.")
            return redirect(self.success_url)
        except Exception as e:
            messages.error(request, f"Error al eliminar el permiso: {str(e)}")
            return redirect(self.success_url)

class GroupModulePermissionDetailView(PermissionMixin, DetailViewMixin, DetailView):
    model = GroupModulePermission
    template_name = 'permission/detail.html'
    context_object_name = 'group_module_permission'
    permission_required = 'view_groupmodulepermission'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        context['breadcrumb_list'] = [
            {'label': 'Inicio', 'url': '/security/'},
            {'label': 'Permisos por Grupo/Módulo', 'url': '/security/group-module-permissions/'},
            {'label': f'Detalle/{obj}', 'url': ''}
        ]
        return context