from apps.security.models import User
from django.contrib.auth.models import Group,Permission

class GroupPermission:
    @staticmethod
    # obtiene los permisos de cada modulo por grupo. Si es superusuario le asigna todos los permisos de cada modulo
    # y si no es superusuario obtiene los permisos del grupo al que pertenece   
    def get_permission_dict_of_group(user: User, group:Group=None):
        if user.is_superuser:
            permissions = list(Permission.objects.all().values_list('codename',flat=True))
            permissions = {x: x for x in permissions if x not in (None, '')}
        elif group is not None:
            # Si el grupo existe, obtener sus permisos
            permissions = list(group.module_permissions.all().values_list('permissions__codename',flat=True))
            permissions = {x: x for x in permissions if x not in (None, '')}
        else:
            # Si no hay grupo asignado, devolver un diccionario vacío
            permissions = {}
        return permissions
    
    @staticmethod
    def debug_user_permissions(user, group, request_path):        
        # Mostrar módulos del grupo
        for gmp in group.module_permissions.all():
            perms = list(gmp.permissions.values_list('codename', flat=True))
        
        # Mostrar permisos directos del usuario
        user_perms = list(user.user_permissions.values_list('codename', flat=True))
