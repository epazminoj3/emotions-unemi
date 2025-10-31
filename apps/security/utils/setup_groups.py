from django.db import transaction
from django.contrib.auth.models import Group
from django.conf import settings

def setup_client_group():
    """
    Configura el grupo 'Clientes' en la base de datos si no existe.
    Este grupo es para usuarios que se registran a través del formulario público.
    """
    with transaction.atomic():
        # Crear o obtener el grupo Clientes
        clients_group, created = Group.objects.get_or_create(name="Clientes")
        
        if created:
            
            try:
                # Intentar configurar la estructura de GroupModulePermission si existe
                from apps.security.models import Module, GroupModulePermission
                
                # Buscar módulos básicos a los que un cliente debería tener acceso
                # Por ejemplo, el dashboard y páginas públicas
                basic_modules = Module.objects.filter(is_active=True, url__in=['', 'dashboard'])
                
                # Para cada módulo básico, crear una entrada en GroupModulePermission sin permisos
                for module in basic_modules:
                    GroupModulePermission.objects.get_or_create(
                        group=clients_group,
                        module=module
                    )
                
            except (ImportError, Exception) as e:
                # Si hay algún error, simplemente crear el grupo sin permisos especiales
                print(f"Aviso: No se pudieron configurar permisos específicos: {e}")
        
        return clients_group
