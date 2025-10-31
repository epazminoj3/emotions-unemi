from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from django.shortcuts import redirect
from django.contrib.auth.models import Group
from apps.security.forms.group_form import GroupForm

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

class GroupListView(PermissionMixin, ListViewMixin, ListView):
    template_name = 'group/list.html'
    model = Group
    context_object_name = 'groups'
    permission_required = 'view_group'
    paginate_by = 10

    def get_queryset(self):
        q = self.request.GET.get('q')
        queryset = self.model.objects.all()
        if q:
            self.query.add(Q(name__icontains=q), Q.AND)
        return queryset.filter(self.query).order_by('id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        breadcrumb_list = [
            {'label': 'Inicio', 'url': '/security/'},
            {'label': 'Lista de Grupos', 'url': ''}
        ]
        context['breadcrumb_list'] = breadcrumb_list
        context['create'] = reverse_lazy('security:group_create')
        context['title'] = 'Gestión de Grupos'
        context['total_groups'] = Group.objects.count()
        context['total_users_in_groups'] = sum([g.user_set.count() for g in Group.objects.all()])
        largest_group = max(Group.objects.all(), key=lambda g: g.user_set.count(), default=None)
        context['largest_group_name'] = largest_group.name if largest_group and largest_group.user_set.count() > 0 else 'N/A'
        return context

class GroupCreateView(PermissionMixin, CreateViewMixin, CreateView):
    model = Group
    template_name = 'group/form.html'
    form_class = GroupForm
    success_url = reverse_lazy('security:group_list')
    permission_required = 'add_group'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = self.get_form()
        context['title'] = 'Crear Grupo'
        context['submit_text'] = 'Guardar Grupo'
        breadcrumb_list = [
            {'label': 'Inicio', 'url': '/security/'},
            {'label': 'Lista de Grupos', 'url': '/security/groups/'},
            {'label': 'Creando Grupo', 'url': ''}
        ]
        context['breadcrumb_list'] = breadcrumb_list
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        group = self.object
        messages.success(self.request, f"Grupo '{group.name}' creado con éxito.")
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.error(self.request, "Error en el formulario.")
        return response

class GroupUpdateView(PermissionMixin, UpdateViewMixin, UpdateView):
    model = Group
    template_name = 'group/form.html'
    form_class = GroupForm
    success_url = reverse_lazy('security:group_list')
    permission_required = 'change_group'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = self.get_form()
        context['title'] = 'Actualizar Grupo'
        context['submit_text'] = 'Actualizar Grupo'
        group = self.object
        breadcrumb_list = [
            {'label': 'Inicio', 'url': '/security/'},
            {'label': 'Lista de Grupos', 'url': '/security/groups/'},
            {'label': f'Actualización/{group.name}', 'url': ''}
        ]
        context['breadcrumb_list'] = breadcrumb_list
        context['object'] = self.get_object()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        group = self.object
        messages.success(self.request, f"Grupo '{group.name}' actualizado con éxito.")
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.error(self.request, "Error en el formulario.")
        return response

class GroupDeleteView(PermissionMixin, DeleteViewMixin, DeleteView):
    model = Group
    success_url = reverse_lazy('security:group_list')
    permission_required = 'delete_group'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Eliminar Grupo: {self.object.name}'
        return context

    def post(self, request, *args, **kwargs):
        group = self.get_object()
        group_name = group.name
        response = super().post(request, *args, **kwargs)
        messages.success(request, f"Grupo '{group_name}' eliminado con éxito.")
        return response

    def delete(self, request, *args, **kwargs):
        group = self.get_object()
        group_name = group.name
        try:
            group.delete()
            messages.success(request, f"Grupo '{group_name}' eliminado con éxito.")
            return redirect(self.success_url)
        except Exception as e:
            messages.error(request, f"Error al eliminar el grupo: {str(e)}")
            return redirect(self.success_url)

class GroupDetailView(PermissionMixin, DetailViewMixin, DetailView):
    model = Group
    template_name = 'group/detail.html'
    context_object_name = 'current_group'
    permission_required = 'view_group'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = self.object
        breadcrumb_list = [
            {'label': 'Inicio', 'url': '/security/'},
            {'label': 'Lista de Grupos', 'url': '/security/groups/'},
            {'label': f'Detalle/{group.name}', 'url': ''}
        ]
        context['breadcrumb_list'] = breadcrumb_list
        messages.success(self.request, f"Bienvenido al grupo '{group.name}'.")
        return context