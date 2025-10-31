from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q, Count
from django.shortcuts import redirect
from apps.security.models import Menu, Module
from apps.security.forms.menu_form import MenuForm

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

class MenuListView(PermissionMixin, ListViewMixin, ListView):
    """
    Vista para listar menús usando el template genérico list.html
    """
    template_name = 'menu/list.html' 
    model = Menu
    context_object_name = 'menus'
    permission_required = 'view_menu'
    paginate_by = 10  

    def get_queryset(self):
        q = self.request.GET.get('q')
        
        # Iniciar con la consulta base
        queryset = self.model.objects.all().annotate(module_count=Count('modules'))
        
        # Filtrar por término de búsqueda
        if q:
            self.query.add(Q(name__icontains=q) | 
                           Q(icon__icontains=q), Q.AND)
        
        return queryset.filter(self.query).order_by('order', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        breadcrumb_list = [
            {'label': 'Inicio', 'url': '/security/'},
            {'label': 'Lista de Menús', 'url': ''}
        ]

        context['breadcrumb_list'] = breadcrumb_list
        
        # URLs para las acciones
        context['create'] = reverse_lazy('security:menu_create')
        
        # Título de la página
        context['title'] = 'Gestión de Menús'
        
        # Estadísticas
        context['total_menus'] = Menu.objects.count()
        context['total_modules'] = Module.objects.count()
        
        return context
    
class MenuCreateView(PermissionMixin, CreateViewMixin, CreateView):    
    """
    Vista para crear menús
    """
    model = Menu
    template_name = 'menu/form.html'
    form_class = MenuForm
    success_url = reverse_lazy('security:menu_list')
    permission_required = 'add_menu'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if 'form' not in context:
            context['form'] = self.get_form()

        context['title'] = 'Crear Menú'
        context['submit_text'] = 'Guardar Menú'

        breadcrumb_list = [
            {'label': 'Inicio', 'url': '/security/'},
            {'label': 'Lista de Menús', 'url': '/security/menus/'},
            {'label': 'Crear Menú', 'url': ''}
        ]

        context['breadcrumb_list'] = breadcrumb_list

        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        menu = self.object
        messages.success(self.request, f"Menú '{menu.name}' creado con éxito.")
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.error(self.request, f"Error en el formulario.")
        return response
        
class MenuUpdateView(PermissionMixin, UpdateViewMixin, UpdateView):    
    """
    Vista para actualizar menús
    """
    model = Menu
    template_name = 'menu/form.html'
    form_class = MenuForm
    success_url = reverse_lazy('security:menu_list')
    permission_required = 'change_menu'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = self.get_form()

        context['title'] = 'Actualizar Menú'
        context['submit_text'] = 'Actualizar Menú'

        menu = self.object

        breadcrumb_list = [
            {'label': 'Inicio', 'url': '/security/'},
            {'label': 'Lista de Menús', 'url': '/security/menus/'},
            {'label': f'Actualizar/{menu.name}', 'url': ''}
        ]

        context['breadcrumb_list'] = breadcrumb_list

        context['object'] = self.get_object()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        menu = self.object
        messages.success(self.request, f"Menú '{menu.name}' actualizado con éxito.")
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.error(self.request, f"Error en el formulario.")
        return response

class MenuDeleteView(PermissionMixin, DeleteViewMixin, DeleteView):
    """
    Vista para eliminar menús
    """
    model = Menu
    success_url = reverse_lazy('security:menu_list')
    permission_required = 'delete_menu'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Eliminar Menú: {self.object.name}'
        return context

    def post(self, request, *args, **kwargs):
        menu = self.get_object()
        menu_name = menu.name
        
        # Verificar si hay módulos asociados
        if menu.modules.exists():
            messages.error(request, f"No se puede eliminar el menú '{menu_name}' porque tiene módulos asociados.")
            return redirect(self.success_url)
        
        response = super().post(request, *args, **kwargs)
        
        messages.success(request, f"Menú '{menu_name}' eliminado con éxito.")
        return response
    
    def delete(self, request, *args, **kwargs):
        """Override para manejar eliminación via AJAX"""
        menu = self.get_object()
        menu_name = menu.name
        
        # Verificar si hay módulos asociados
        if menu.modules.exists():
            messages.error(request, f"No se puede eliminar el menú '{menu_name}' porque tiene módulos asociados.")
            return redirect(self.success_url)
        
        try:
            menu.delete()
            messages.success(request, f"Menú '{menu_name}' eliminado con éxito.")
            return redirect(self.success_url)
        except Exception as e:
            messages.error(request, f"Error al eliminar el menú: {str(e)}")
            return redirect(self.success_url)

class MenuDetailView(PermissionMixin, DetailViewMixin, DetailView):
    """
    Vista para ver detalles de un menú
    """
    model = Menu
    template_name = 'menu/detail.html'
    context_object_name = 'menu'
    permission_required = 'view_menu'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        menu = self.get_object()

        # Obtener todos los módulos asociados a este menú
        context['modules'] = Module.objects.filter(menu=menu).order_by('order', 'name')

        breadcrumb_list = [
            {'label': 'Inicio', 'url': '/security/'},
            {'label': 'Lista de Menús', 'url': '/security/menus/'},
            {'label': f'Detalle/{menu.name}', 'url': ''}
        ]

        context['breadcrumb_list'] = breadcrumb_list
        
        return context
