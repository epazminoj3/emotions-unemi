from django.contrib.auth import views as auth_views, get_user_model
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render, redirect
from django import forms

User = get_user_model()

class EmailValidationPasswordResetForm(auth_views.PasswordResetForm):
    """Formulario personalizado que valida si el correo existe antes de enviar el email"""
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("No hay ninguna cuenta registrada con este correo electrónico.")
        return email

class CustomPasswordResetView(auth_views.PasswordResetView):
    """Vista personalizada para solicitud de restablecimiento de contraseña"""
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('security:password_reset_done')
    form_class = EmailValidationPasswordResetForm

class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    """Vista personalizada para confirmación de envío de correo de restablecimiento"""
    template_name = 'registration/password_reset_done.html'

class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    """Vista personalizada para formulario de nueva contraseña"""
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('security:password_reset_complete')

class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    """Vista personalizada para confirmación de restablecimiento exitoso"""
    template_name = 'registration/password_reset_complete.html'
