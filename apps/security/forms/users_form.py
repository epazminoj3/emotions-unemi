from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from apps.security.models import User


class UserForm(UserCreationForm):
    """
    Formulario para crear y editar usuarios
    """
    
    # Campos personalizados
    image = forms.ImageField(
        label='Imagen de perfil',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
        })
    )
    
    first_name = forms.CharField(
        max_length=150,
        label='Nombres',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese los nombres',
            'autocomplete': 'given-name'
        })
    )
    
    last_name = forms.CharField(
        max_length=150,
        label='Apellidos',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese los apellidos',
            'autocomplete': 'family-name'
        })
    )
    
    username = forms.CharField(
        max_length=150,
        label='Nombre de usuario',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese el nombre de usuario',
            'autocomplete': 'username'
        })
    )
    
    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'usuario@ejemplo.com',
            'autocomplete': 'email'
        })
    )
    
    dni = forms.CharField(
        max_length=20,
        label='Cédula/DNI',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese la cédula o DNI',
            'autocomplete': 'off'
        })
    )
    
    phone = forms.CharField(
        max_length=20,
        label='Teléfono',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+593 99 123 4567',
            'autocomplete': 'tel'
        })
    )
    
    address = forms.CharField(
        max_length=255,
        label='Dirección',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese la dirección completa',
            'rows': 3,
            'autocomplete': 'street-address'
        })
    )
    
    date_of_birth = forms.DateField(
        label='Fecha de nacimiento',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'autocomplete': 'bday'
        })
    )
    
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        label='Grupos',
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control select-multiple',
            'size': '5'
        }),
        help_text='Seleccione los grupos a los que pertenece el usuario'
    )
    
    is_active = forms.BooleanField(
        label='Usuario activo',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    is_staff = forms.BooleanField(
        label='Es staff',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Permite al usuario acceder al sitio de administración'
    )

    is_superuser = forms.BooleanField(
        label='Es superusuario',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Permite al usuario tener todos los permisos'
    )
    
    password1 = forms.CharField(
        label='Contraseña',
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese la contraseña',
            'autocomplete': 'new-password'
        }),
        help_text='La contraseña debe tener al menos 8 caracteres'
    )
    
    password2 = forms.CharField(
        label='Confirmar contraseña',
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme la contraseña',
            'autocomplete': 'new-password'
        })
    )

    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email', 'dni', 
            'phone', 'address', 'date_of_birth', 'groups', 
            'is_active', 'is_staff', 'is_superuser', 'password1', 'password2',
            'image'
        ]

    def __init__(self, *args, **kwargs):
        """
        Inicialización del formulario
        """
        super().__init__(*args, **kwargs)
        
        # Si estamos editando un usuario existente
        if self.instance and self.instance.pk:
            # Hacer las contraseñas opcionales para edición
            self.fields['password1'].required = False
            self.fields['password2'].required = False
            self.fields['password1'].help_text = 'Deje en blanco si no desea cambiar la contraseña'
            self.fields['password2'].help_text = 'Confirme la nueva contraseña si la cambió'
            
            # Preseleccionar los grupos actuales
            if self.instance.groups.exists():
                self.fields['groups'].initial = self.instance.groups.all()

    def clean_email(self):
        """
        Validar que el email sea único
        """
        email = self.cleaned_data.get('email')
        if email:
            # Verificar si el email ya existe
            queryset = User.objects.filter(email=email)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise forms.ValidationError('Ya existe un usuario con este correo electrónico.')
        
        return email

    def clean_username(self):
        """
        Validar que el username sea único
        """
        username = self.cleaned_data.get('username')
        if username:
            # Verificar si el username ya existe
            queryset = User.objects.filter(username=username)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise forms.ValidationError('Ya existe un usuario con este nombre de usuario.')
        
        return username

    def clean_dni(self):
        """
        Validar que el DNI sea único si se proporciona
        """
        dni = self.cleaned_data.get('dni')
        if dni:
            # Verificar si el DNI ya existe
            queryset = User.objects.filter(dni=dni)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise forms.ValidationError('Ya existe un usuario con esta cédula/DNI.')
        
        return dni

    def clean_password2(self):
        """
        Validar que las contraseñas coincidan y sean requeridas
        """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        # Ambas contraseñas son requeridas siempre
        if not password1:
            raise forms.ValidationError("La contraseña es requerida.")
        if not password2:
            raise forms.ValidationError("Debe confirmar la contraseña.")

        if password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")

        # Validar longitud mínima
        if len(password1) < 8:
            raise forms.ValidationError("La contraseña debe tener al menos 8 caracteres.")

        return password2

    def save(self, commit=True):
        """
        Guardar el usuario
        """
        user = super().save(commit=False)

        # Establecer la nueva contraseña siempre
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()
            # Guardar los grupos
            if 'groups' in self.cleaned_data:
                user.groups.set(self.cleaned_data['groups'])

        return user
