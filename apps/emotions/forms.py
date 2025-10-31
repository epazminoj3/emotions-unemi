"""
Formularios para la aplicación de detección de emociones.
"""
from django import forms
from django.core.exceptions import ValidationError
from .models import EmotionAnalysis


class EmotionAnalysisForm(forms.ModelForm):
    """
    Formulario para subir imágenes para análisis de emociones.
    """
    
    class Meta:
        model = EmotionAnalysis
        fields = ['image', 'notes']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none',
                'accept': 'image/*',
                'id': 'image-upload'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'block w-full p-2.5 text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500',
                'rows': 3,
                'placeholder': 'Notas adicionales sobre el análisis (opcional)...'
            })
        }
        labels = {
            'image': 'Imagen para Análisis',
            'notes': 'Notas (Opcional)'
        }
        help_texts = {
            'image': 'Selecciona una imagen que contenga rostros para analizar las emociones.',
            'notes': 'Puedes agregar cualquier observación o contexto sobre la imagen.'
        }
    
    def clean_image(self):
        """
        Valida que el archivo subido sea una imagen válida.
        """
        image = self.cleaned_data.get('image')
        
        if image:
            # Verificar el tamaño del archivo (máximo 10MB)
            if image.size > 10 * 1024 * 1024:  # 10MB en bytes
                raise ValidationError('El archivo es demasiado grande. El tamaño máximo permitido es 10MB.')
            
            # Verificar el tipo de archivo
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp']
            if hasattr(image, 'content_type') and image.content_type not in allowed_types:
                raise ValidationError('Tipo de archivo no válido. Solo se permiten imágenes JPEG, PNG, GIF o BMP.')
            
            # Verificar la extensión del archivo
            import os
            ext = os.path.splitext(image.name)[1].lower()
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
            if ext not in allowed_extensions:
                raise ValidationError('Extensión de archivo no válida. Use: jpg, jpeg, png, gif, bmp.')
        
        return image


class ImageUploadForm(forms.Form):
    """
    Formulario simple para subir imágenes sin guardar en base de datos.
    """
    
    image = forms.ImageField(
        label='Seleccionar Imagen',
        widget=forms.FileInput(attrs={
            'class': 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none',
            'accept': 'image/*',
            'id': 'quick-image-upload'
        }),
        help_text='Selecciona una imagen para análisis rápido de emociones.'
    )
    
    def clean_image(self):
        """
        Valida que el archivo subido sea una imagen válida.
        """
        image = self.cleaned_data.get('image')
        
        if image:
            # Verificar el tamaño del archivo (máximo 5MB para análisis rápido)
            if image.size > 5 * 1024 * 1024:  # 5MB en bytes
                raise ValidationError('El archivo es demasiado grande. El tamaño máximo para análisis rápido es 5MB.')
            
            # Verificar el tipo de archivo
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if hasattr(image, 'content_type') and image.content_type not in allowed_types:
                raise ValidationError('Tipo de archivo no válido. Solo se permiten imágenes JPEG, PNG o GIF.')
        
        return image


class CameraAnalysisForm(forms.Form):
    """
    Formulario para análisis desde cámara web (base64).
    """
    
    image_data = forms.CharField(
        widget=forms.HiddenInput(),
        required=True
    )
    
    save_analysis = forms.BooleanField(
        required=False,
        initial=True,
        label='Guardar análisis',
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
        }),
        help_text='Marcar para guardar este análisis en tu historial.'
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'block w-full p-2.5 text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500',
            'rows': 2,
            'placeholder': 'Notas sobre esta captura (opcional)...'
        }),
        label='Notas (Opcional)'
    )
    
    def clean_image_data(self):
        """
        Valida que los datos de imagen base64 sean válidos.
        """
        image_data = self.cleaned_data.get('image_data')
        
        if image_data:
            # Verificar que tenga el formato correcto de base64
            if not image_data.startswith('data:image/'):
                raise ValidationError('Datos de imagen no válidos.')
            
            # Verificar que no esté vacío después del header
            if len(image_data.split(',')) < 2:
                raise ValidationError('Datos de imagen incompletos.')
        
        return image_data