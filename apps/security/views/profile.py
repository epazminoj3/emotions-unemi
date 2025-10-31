from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import DetailView, UpdateView
from apps.security.models import User
from apps.security.forms.profile_form import UserProfileForm

class UserProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'profile/detail.html'
    
    def get_object(self, queryset=None):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Mi Perfil'
        context['breadcrumb_list'] = [
            {'label': 'Inicio', 'url': '/security/'},
            {'label': 'Mi Perfil', 'url': ''}
        ]
        return context

class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'profile/form.html'
    success_url = reverse_lazy('security:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Actualizar Perfil'
        context['submit_text'] = 'Guardar Cambios'
        context['breadcrumb_list'] = [
            {'label': 'Inicio', 'url': '/security/'},
            {'label': 'Mi Perfil', 'url': reverse_lazy('security:profile')},
            {'label': 'Actualizar', 'url': ''}
        ]
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Perfil actualizado correctamente.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Error al actualizar el perfil.")
        return super().form_invalid(form)