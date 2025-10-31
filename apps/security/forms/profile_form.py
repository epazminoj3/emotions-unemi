from django import forms
from apps.security.models import User

class UserProfileForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Nueva contraseña',
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-lg border border-neutral-300 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 shadow-sm transition duration-200 text-sm placeholder-neutral-400',
            'placeholder': 'Ingrese nueva contraseña',
            'autocomplete': 'new-password'
        })
    )
    password2 = forms.CharField(
        label='Confirmar nueva contraseña',
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-lg border border-neutral-300 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 shadow-sm transition duration-200 text-sm placeholder-neutral-400',
            'placeholder': 'Confirme nueva contraseña',
            'autocomplete': 'new-password'
        })
    )

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'dni', 'phone', 'direction', 'image'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-lg border border-neutral-300 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 shadow-sm transition duration-200 text-sm placeholder-neutral-400',
                'placeholder': 'Ingrese sus nombres'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-lg border border-neutral-300 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 shadow-sm transition duration-200 text-sm placeholder-neutral-400',
                'placeholder': 'Ingrese sus apellidos'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-lg border border-neutral-300 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 shadow-sm transition duration-200 text-sm placeholder-neutral-400',
                'placeholder': 'correo@ejemplo.com'
            }),
            'dni': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-lg border border-neutral-300 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 shadow-sm transition duration-200 text-sm placeholder-neutral-400',
                'placeholder': 'Ingrese su número de identificación'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-lg border border-neutral-300 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 shadow-sm transition duration-200 text-sm placeholder-neutral-400',
                'placeholder': 'Ingrese su número de teléfono'
            }),
            'direction': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-lg border border-neutral-300 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 shadow-sm transition duration-200 text-sm placeholder-neutral-400',
                'placeholder': 'Ingrese su dirección'
            }),
            'image': forms.FileInput(attrs={
                'class': 'w-full text-sm text-neutral-600 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100 border border-neutral-300 rounded-lg cursor-pointer focus:outline-none',
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 or password2:
            if password1 != password2:
                self.add_error('password2', 'Las contraseñas no coinciden.')
            if password1 and len(password1) < 8:
                self.add_error('password1', 'La contraseña debe tener al menos 8 caracteres.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password1 = self.cleaned_data.get('password1')
        if password1:
            user.set_password(password1)
        if commit:
            user.save()
        return user