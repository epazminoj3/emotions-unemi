# apps/security/forms/system_config_form.py
from django import forms
from apps.security.models import SystemConfig


class SystemConfigForm(forms.ModelForm):
    """
    Formulario para crear y editar configuración del sistema con estilos Tailwind profesionales
    """
    
    name = forms.CharField(
        max_length=100,
        label='Nombre del sistema',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-neutral-200 rounded-xl '
                    'text-neutral-800 placeholder-neutral-400 '
                    'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent '
                    'hover:border-neutral-300 transition-all duration-200 ease-in-out '
                    'shadow-sm hover:shadow-md',
            'placeholder': 'Ingrese el nombre del sistema',
            'autocomplete': 'off'
        })
    )
    
    description = forms.CharField(
        label='Descripción',
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-neutral-200 rounded-xl '
                    'text-neutral-800 placeholder-neutral-400 '
                    'focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-transparent '
                    'hover:border-neutral-300 transition-all duration-200 ease-in-out '
                    'shadow-sm hover:shadow-md',
            'placeholder': 'Descripción del sistema',
            'rows': '4',
            'autocomplete': 'off'
        })
    )
    
    icon = forms.CharField(
        max_length=50,
        label='Icono',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-neutral-200 rounded-xl '
                    'text-neutral-800 placeholder-neutral-400 '
                    'focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-transparent '
                    'hover:border-neutral-300 transition-all duration-200 ease-in-out '
                    'shadow-sm hover:shadow-md',
            'placeholder': 'Ej: fas fa-bolt',
            'autocomplete': 'off'
        })
    )
    
    logo = forms.ImageField(
        label='Logo',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-neutral-200 rounded-xl '
                    'text-neutral-800 placeholder-neutral-400 '
                    'focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-transparent '
                    'hover:border-neutral-300 transition-all duration-200 ease-in-out '
                    'shadow-sm hover:shadow-md',
        }),
        help_text='Seleccione un logo para el sistema (opcional)'
    )
    
    company = forms.CharField(
        max_length=100,
        label='Nombre de la empresa',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-neutral-200 rounded-xl '
                    'text-neutral-800 placeholder-neutral-400 '
                    'focus:outline-none focus:ring-2 focus:ring-secondary-500 focus:border-transparent '
                    'hover:border-neutral-300 transition-all duration-200 ease-in-out '
                    'shadow-sm hover:shadow-md',
            'placeholder': 'Nombre de la empresa',
            'autocomplete': 'off'
        })
    )
    
    year = forms.IntegerField(
        label='Año',
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-neutral-200 rounded-xl '
                    'text-neutral-800 placeholder-neutral-400 '
                    'focus:outline-none focus:ring-2 focus:ring-secondary-500 focus:border-transparent '
                    'hover:border-neutral-300 transition-all duration-200 ease-in-out '
                    'shadow-sm hover:shadow-md',
            'placeholder': 'Año actual',
            'min': '2000',
            'max': '2100',
        })
    )

    class Meta:
        model = SystemConfig
        fields = ['name', 'description', 'icon', 'logo', 'company', 'year']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Aplicar estilos personalizados a las etiquetas
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'data-field': field_name,
            })
            
            # Personalizar estilos específicos por campo
            if field_name == 'name':
                field.widget.attrs['class'] += ' focus:ring-primary-500'
            elif field_name in ['icon', 'description', 'logo']:
                field.widget.attrs['class'] += ' focus:ring-accent-500'
            elif field_name in ['company', 'year']:
                field.widget.attrs['class'] += ' focus:ring-secondary-500'