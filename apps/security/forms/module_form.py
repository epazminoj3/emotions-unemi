from django import forms
from django.contrib.auth.models import Permission
from apps.security.models import Module, Menu

class ModuleForm(forms.ModelForm):
    """
    Formulario para crear y editar módulos con estilos Tailwind y selección de permisos filtrable.
    """
    name = forms.CharField(
        max_length=100,
        label='Nombre del módulo',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-neutral-200 rounded-xl '
                     'text-neutral-800 placeholder-neutral-400 '
                     'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent '
                     'hover:border-neutral-300 transition-all duration-200 ease-in-out '
                     'shadow-sm hover:shadow-md',
            'placeholder': 'Ingrese el nombre del módulo',
            'autocomplete': 'off'
        })
    )
    url = forms.CharField(
        max_length=100,
        label='URL',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-neutral-200 rounded-xl '
                     'text-neutral-800 placeholder-neutral-400 '
                     'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent '
                     'hover:border-neutral-300 transition-all duration-200 ease-in-out '
                     'shadow-sm hover:shadow-md',
            'placeholder': 'Ejemplo: clientes/',
            'autocomplete': 'off'
        })
    )
    menu = forms.ModelChoiceField(
        queryset=Menu.objects.all(),
        label='Menú',
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-neutral-200 rounded-xl '
                     'text-neutral-800 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent '
                     'hover:border-neutral-300 transition-all duration-200 ease-in-out shadow-sm hover:shadow-md'
        })
    )
    description = forms.CharField(
        max_length=200,
        label='Descripción',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-neutral-200 rounded-xl '
                     'text-neutral-800 placeholder-neutral-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent '
                     'hover:border-neutral-300 transition-all duration-200 ease-in-out shadow-sm hover:shadow-md',
            'placeholder': 'Descripción del módulo',
            'rows': 2
        })
    )
    icon = forms.CharField(
        max_length=100,
        label='Icono',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-neutral-200 rounded-xl '
                     'text-neutral-800 placeholder-neutral-400 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-transparent '
                     'hover:border-neutral-300 transition-all duration-200 ease-in-out shadow-sm hover:shadow-md',
            'placeholder': 'Ej: fas fa-user',
            'autocomplete': 'off'
        })
    )
    is_active = forms.BooleanField(
        label='¿Está activo?',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'accent-primary-500 rounded'
        })
    )
    order = forms.IntegerField(
        label='Orden',
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-neutral-200 rounded-xl text-neutral-800 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent hover:border-neutral-300 transition-all duration-200 ease-in-out shadow-sm hover:shadow-md',
            'min': 0
        })
    )
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        required=False,
        label='Permisos',
    )

    class Meta:
        model = Module
        fields = ['name', 'url', 'menu', 'description', 'icon', 'is_active', 'order', 'permissions']