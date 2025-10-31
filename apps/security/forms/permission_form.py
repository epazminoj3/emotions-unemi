from django import forms
from django.contrib.auth.models import Group, Permission
from apps.security.models import Module, GroupModulePermission

class GroupModulePermissionCreateForm(forms.ModelForm):
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        label='Grupo',
        widget=forms.Select(attrs={'class': 'w-full px-4 py-3 bg-white border border-neutral-200 rounded-xl'})
    )
    module = forms.ModelChoiceField(
        queryset=Module.objects.all(),
        label='Módulo',
        widget=forms.Select(attrs={'class': 'w-full px-4 py-3 bg-white border border-neutral-200 rounded-xl'})
    )
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.none(),
        required=False,
        label='Permisos',
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'accent-indigo-500'})
    )

    class Meta:
        model = GroupModulePermission
        fields = ['group', 'module', 'permissions']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtra los permisos según el módulo seleccionado
        if 'module' in self.data:
            try:
                module_id = int(self.data.get('module'))
                module = Module.objects.get(pk=module_id)
                self.fields['permissions'].queryset = module.permissions.all()
            except (ValueError, Module.DoesNotExist):
                self.fields['permissions'].queryset = Permission.objects.none()
        elif self.initial.get('module'):
            module = self.initial['module']
            self.fields['permissions'].queryset = module.permissions.all()
        else:
            self.fields['permissions'].queryset = Permission.objects.none()

class GroupModulePermissionEditForm(forms.ModelForm):
    """
    Formulario para edición individual de permisos de grupo sobre módulo.
    Solo permite editar los permisos, grupo y módulo son solo lectura.
    """
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.none(),
        required=False,
        label='Permisos',
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'accent-indigo-500'
        })
    )

    class Meta:
        model = GroupModulePermission
        fields = ['permissions']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.module:
            self.fields['permissions'].queryset = self.instance.module.permissions.all()
            self.fields['permissions'].initial = self.instance.permissions.all()