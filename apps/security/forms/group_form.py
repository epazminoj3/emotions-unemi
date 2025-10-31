from django import forms
from django.contrib.auth.models import Group, Permission
from django.utils.text import capfirst

class GroupForm(forms.ModelForm):
    """
    Formulario para crear y editar grupos con estilos Tailwind profesionales,
    incluyendo la asignación de permisos con checkboxes agrupados por modelo.
    """

    name = forms.CharField(
        max_length=150,
        label='Nombre del grupo',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-neutral-200 rounded-xl '
                     'text-neutral-800 placeholder-neutral-400 '
                     'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent '
                     'hover:border-neutral-300 transition-all duration-200 ease-in-out '
                     'shadow-sm hover:shadow-md',
            'placeholder': 'Ingrese el nombre del grupo',
            'autocomplete': 'off'
        })
    )

    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.select_related('content_type').order_by('content_type__model', 'codename'),
        required=False,
        label='Permisos',
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'mr-2 accent-primary-500'
        }),
        help_text='Seleccione los permisos que desea asignar al grupo.'
    )

    class Meta:
        model = Group
        fields = ['name', 'permissions']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'data-field': field_name,
            })
            if field_name == 'name':
                field.widget.attrs['class'] += ' focus:ring-primary-500'
            elif field_name == 'permissions':
                field.widget.attrs['class'] += ' focus:ring-accent-500'

        # Agrupar permisos por modelo para el template
        self.permission_groups = {}
        for perm in self.fields['permissions'].queryset:
            model = capfirst(perm.content_type.model)
            if model not in self.permission_groups:
                self.permission_groups[model] = []
            self.permission_groups[model].append(perm)