from django import forms
from apps.security.models import Menu


class MenuForm(forms.ModelForm):
    """
    Formulario para crear y editar menús con estilos Tailwind profesionales
    """
    
    name = forms.CharField(
        max_length=150,
        label='Nombre del menú',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-neutral-200 rounded-xl '
                    'text-neutral-800 placeholder-neutral-400 '
                    'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent '
                    'hover:border-neutral-300 transition-all duration-200 ease-in-out '
                    'shadow-sm hover:shadow-md',
            'placeholder': 'Ingrese el nombre del menú',
            'autocomplete': 'off'
        })
    )
    
    icon = forms.CharField(
        max_length=100,
        label='Icono',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-neutral-200 rounded-xl '
                    'text-neutral-800 placeholder-neutral-400 '
                    'focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-transparent '
                    'hover:border-neutral-300 transition-all duration-200 ease-in-out '
                    'shadow-sm hover:shadow-md',
            'placeholder': 'Ej: fas fa-home',
            'autocomplete': 'off'
        })
    )
    
    order = forms.IntegerField(
        label='Orden de visualización',
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-neutral-200 rounded-xl '
                    'text-neutral-800 placeholder-neutral-400 '
                    'focus:outline-none focus:ring-2 focus:ring-secondary-500 focus:border-transparent '
                    'hover:border-neutral-300 transition-all duration-200 ease-in-out '
                    'shadow-sm hover:shadow-md',
            'placeholder': 'Orden de visualización',
            'min': '0',
            'step': '1'
        }),
        help_text='Define el orden en que aparece en el menú (menor número = mayor prioridad)'
    )

    class Meta:
        model = Menu
        fields = ['name', 'icon', 'order']

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
            elif field_name == 'icon':
                field.widget.attrs['class'] += ' focus:ring-accent-500'
            elif field_name == 'order':
                field.widget.attrs['class'] += ' focus:ring-secondary-500'