from django.contrib import admin
from .models import EmotionAnalysis, EmotionStatistics


@admin.register(EmotionAnalysis)
class EmotionAnalysisAdmin(admin.ModelAdmin):
    """
    Administrador para el modelo EmotionAnalysis.
    """
    list_display = [
        'user', 'faces_detected', 'dominant_emotion', 
        'average_confidence', 'created_at', 'processing_time'
    ]
    list_filter = [
        'dominant_emotion', 'created_at', 'faces_detected'
    ]
    search_fields = [
        'user__username', 'user__email', 'dominant_emotion', 'notes'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'processing_time'
    ]
    ordering = ['-created_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('user', 'image', 'notes')
        }),
        ('Resultados del Análisis', {
            'fields': (
                'faces_detected', 'dominant_emotion', 
                'average_confidence', 'analysis_results'
            )
        }),
        ('Metadatos', {
            'fields': ('processing_time', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        """
        Optimizar consultas incluyendo el usuario.
        """
        return super().get_queryset(request).select_related('user')
    
    def has_change_permission(self, request, obj=None):
        """
        Limitar edición de análisis completados.
        """
        if obj and obj.analysis_results:
            return False  # No permitir editar análisis ya procesados
        return super().has_change_permission(request, obj)


@admin.register(EmotionStatistics)
class EmotionStatisticsAdmin(admin.ModelAdmin):
    """
    Administrador para el modelo EmotionStatistics.
    """
    list_display = [
        'user', 'total_analyses', 'total_faces_detected',
        'most_frequent_emotion', 'average_confidence', 'last_updated'
    ]
    list_filter = [
        'most_frequent_emotion', 'last_updated'
    ]
    search_fields = [
        'user__username', 'user__email'
    ]
    readonly_fields = [
        'total_analyses', 'total_faces_detected', 'neutral_count',
        'happiness_count', 'surprise_count', 'sadness_count',
        'anger_count', 'disgust_count', 'fear_count', 'contempt_count',
        'most_frequent_emotion', 'average_confidence',
        'average_faces_per_analysis', 'last_updated'
    ]
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Estadísticas Generales', {
            'fields': (
                'total_analyses', 'total_faces_detected',
                'average_faces_per_analysis', 'average_confidence'
            )
        }),
        ('Distribución de Emociones', {
            'fields': (
                'neutral_count', 'happiness_count', 'surprise_count',
                'sadness_count', 'anger_count', 'disgust_count',
                'fear_count', 'contempt_count', 'most_frequent_emotion'
            )
        }),
        ('Metadatos', {
            'fields': ('last_updated',)
        })
    )
    
    def has_add_permission(self, request):
        """
        No permitir crear estadísticas manualmente.
        """
        return False
    
    def has_change_permission(self, request, obj=None):
        """
        Solo permitir ver las estadísticas.
        """
        return False
    
    def has_delete_permission(self, request, obj=None):
        """
        No permitir eliminar estadísticas.
        """
        return False
    
    actions = ['update_statistics']
    
    def update_statistics(self, request, queryset):
        """
        Acción para actualizar estadísticas seleccionadas.
        """
        updated = 0
        for stats in queryset:
            stats.update_statistics()
            updated += 1
        
        self.message_user(
            request,
            f"Se actualizaron {updated} registros de estadísticas."
        )
    
    update_statistics.short_description = "Actualizar estadísticas seleccionadas"
