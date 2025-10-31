from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from django.shortcuts import redirect
from apps.security.models import User
from apps.security.forms.users_form import UserForm

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

class UserListView(PermissionMixin, ListViewMixin, ListView):
    """
    Vista para listar usuarios usando el template genérico list.html
    """
    template_name = 'user/list.html' 
    model = User
    context_object_name = 'users'
    permission_required = 'view_user'
    paginate_by = 10  

    def get_queryset(self):
        q = self.request.GET.get('q')
        
        # Iniciar con la consulta base
        queryset = self.model.objects.all().prefetch_related('groups')
        
        # Filtrar por término de búsqueda
        if q:
            self.query.add(Q(username__icontains=q) | 
                           Q(first_name__icontains=q) | 
                           Q(last_name__icontains=q) | 
                           Q(email__icontains=q) | 
                           Q(dni__icontains=q), Q.AND)
        
        return queryset.filter(self.query).order_by('id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        breadcrumb_list = [
            {'label': 'Inicio', 'url': '/security/'},
            {'label': 'Lista de Usuarios', 'url': ''}
        ]

        context['breadcrumb_list'] = breadcrumb_list
        
        # URLs para las acciones (URLs reales, no cadenas de texto)
        context['create'] = reverse_lazy('security:user_create')
        
        # Título de la página
        context['title'] = 'Gestión de Usuarios'
        
        # Estadísticas
        context['total_users'] = User.objects.count()
        context['active_users'] = User.objects.filter(is_active=True).count()
        context['staff_users'] = User.objects.filter(is_staff=True).count()
        
        return context
    
class UserCreateView(PermissionMixin, CreateViewMixin, CreateView):    
    """
    Vista para crear usuarios
    """
    model = User
    template_name = 'user/form.html'
    form_class = UserForm
    success_url = reverse_lazy('security:user_list')
    permission_required = 'add_user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if 'form' not in context:
            context['form'] = self.get_form()

        context['title'] = 'Crear Usuario'
        context['submit_text'] = 'Guardar Usuario'

        breadcrumb_list = [
            {'label': 'Inicio', 'url': '/security/'},
            {'label': 'Lista de Usuarios', 'url': '/security/users/'},
            {'label': 'Creando Usuario', 'url': ''}
        ]

        context['breadcrumb_list'] = breadcrumb_list

        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object
        messages.success(self.request, f"Usuario {user.get_full_name()} creado con éxito.")
        return response

    def form_invalid(self, form):
        response =  super().form_invalid(form)

        messages.error(self.request, f"Error en el formulario.")

        return response
        
class UserUpdateView(PermissionMixin, UpdateViewMixin, UpdateView):    
    """
    Vista para actualizar usuarios
    """
    model = User
    template_name = 'user/form.html'
    form_class = UserForm
    success_url = reverse_lazy('security:user_list')
    permission_required = 'change_user'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = self.get_form()

        context['title'] = 'Actualizar Usuario'
        context['submit_text'] = 'Actualizar Usuario'

        user = self.object
        user_name = user.get_full_name()

        breadcrumb_list = [
            {'label': 'Inicio', 'url': '/security/'},
            {'label': 'Lista de Usuarios', 'url': '/security/users/'},
            {'label': f'Actualizacion/{user_name}', 'url': ''}
        ]

        context['breadcrumb_list'] = breadcrumb_list

        context['object'] = self.get_object()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object
        messages.success(self.request, f"Usuario {user.get_full_name()} actualizado con éxito.")
        return response

    def form_invalid(self, form):
        response =  super().form_invalid(form)

        messages.error(self.request, f"Error en el formulario.")

        return response

class UserDeleteView(PermissionMixin, DeleteViewMixin, DeleteView):
    """
    Vista para eliminar usuarios
    """
    model = User
    success_url = reverse_lazy('security:user_list')
    permission_required = 'delete_user'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Eliminar Usuario: {self.object.get_full_name()}'
        return context

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        user_name = user.get_full_name()
        
        response = super().post(request, *args, **kwargs)
        
        messages.success(request, f"Usuario {user_name} eliminado con éxito.")
        return response
    
    def delete(self, request, *args, **kwargs):
        """Override para manejar eliminación via AJAX"""
        user = self.get_object()
        user_name = user.get_full_name
        
        try:
            user.delete()

            messages.success(request, f"Usuario {user_name} eliminado con éxito.")
            
            return redirect(self.success_url)
        except Exception as e:
            messages.error(request, f"Error al eliminar el usuario: {str(e)}")
            return redirect(self.success_url)


class UserDetailView(PermissionMixin, DetailViewMixin, DetailView):
    """
    Vista para ver detalles de un usuario
    """
    model = User
    template_name = 'user/detail.html'
    context_object_name = 'current_user'
    permission_required = 'view_user'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.object
        user_name = user.get_full_name()

        breadcrumb_list = [
            {'label': 'Inicio', 'url': '/security/'},
            {'label': 'Lista de Usuarios', 'url': '/security/users/'},
            {'label': f'Detalle/{user_name}', 'url': ''}
        ]

        context['breadcrumb_list'] = breadcrumb_list

        messages.success(self.request, f"Bienvenido '{user_name}'.")

        print("DEBUG context['user']:", context.get('user'))
        print("DEBUG self.object:", self.object)
        
        return context