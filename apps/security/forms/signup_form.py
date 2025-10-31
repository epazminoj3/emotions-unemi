from django import forms
from django.contrib.auth.forms import UserCreationForm
from apps.security.models import User

class SignupForm(UserCreationForm):
    """Formulario para registro de nuevos usuarios"""
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-lg border border-neutral-300 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 shadow-sm transition duration-200 text-sm placeholder-neutral-400',
            'placeholder': 'correo@ejemplo.com'
        }),
        required=True,
        help_text="Requerido. Ingrese una dirección de email válida."
    )
    
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-lg border border-neutral-300 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 shadow-sm transition duration-200 text-sm placeholder-neutral-400',
            'placeholder': 'Ingrese sus nombres'
        }),
        required=True,
    )
    
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-lg border border-neutral-300 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 shadow-sm transition duration-200 text-sm placeholder-neutral-400',
            'placeholder': 'Ingrese sus apellidos'
        }),
        required=True,
    )
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-lg border border-neutral-300 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 shadow-sm transition duration-200 text-sm placeholder-neutral-400',
            'placeholder': 'Ingrese un nombre de usuario'
        }),
        help_text="Requerido. 150 caracteres como máximo. Letras, dígitos y @/./+/-/_ solamente."
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-lg border border-neutral-300 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 shadow-sm transition duration-200 text-sm placeholder-neutral-400',
            'placeholder': 'Ingrese una contraseña segura'
        }),
        help_text="Su contraseña debe tener al menos 8 caracteres y no puede ser demasiado común."
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-lg border border-neutral-300 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 shadow-sm transition duration-200 text-sm placeholder-neutral-400',
            'placeholder': 'Confirme su contraseña'
        }),
        help_text="Ingrese la misma contraseña para verificación."
    )
    
    dni = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-lg border border-neutral-300 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 shadow-sm transition duration-200 text-sm placeholder-neutral-400',
            'placeholder': 'Ingrese su número de identificación'
        }),
        required=False,
    )
    
    phone = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-lg border border-neutral-300 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 shadow-sm transition duration-200 text-sm placeholder-neutral-400',
            'placeholder': 'Ingrese su número telefónico'
        }),
        required=False,
    )
    
    direction = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-lg border border-neutral-300 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 shadow-sm transition duration-200 text-sm placeholder-neutral-400',
            'placeholder': 'Ingrese su dirección'
        }),
        required=False,
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'dni', 'phone', 'direction')
    
    def clean_email(self):
        """Valida que el email no exista ya en la base de datos"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return email
