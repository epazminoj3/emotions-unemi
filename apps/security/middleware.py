from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import Group

class GroupSessionMiddleware(MiddlewareMixin):
    """
    Middleware para manejar los permisos basados en grupo del usuario.
    Agrega la información de módulos y permisos a la solicitud para que esté disponible en las vistas y plantillas.
    """
    def process_request(self, request):
        if not request.user.is_authenticated:
            return None

        # Intentar obtener los modelos necesarios
        try:
            from apps.security.models import GroupModulePermission, Module, Menu
            
            # Verificar si hay un grupo activo en la sesión
            if 'group_id' in request.session:
                try:
                    group_id = request.session['group_id']
                    group = Group.objects.get(pk=group_id)
                    
                    # Verificar que el usuario pertenezca a este grupo
                    if group not in request.user.groups.all():
                        # Si no pertenece, eliminar de la sesión
                        del request.session['group_id']
                        # Y usar el primer grupo al que pertenezca
                        if request.user.groups.exists():
                            group = request.user.groups.first()
                            request.session['group_id'] = group.id
                        else:
                            return None
                    
                    # Establecer el grupo activo en la solicitud
                    request.active_group = group
                    
                    # Obtener los módulos y permisos del grupo activo
                    group_module_permissions = GroupModulePermission.objects.filter(
                        group=group, 
                        module__is_active=True
                    ).select_related('module', 'module__menu').prefetch_related('permissions')
                    
                    # Crear listas para almacenar los módulos y permisos
                    request.user_modules = []
                    request.user_permissions = set()
                    request.menu_list = []
                    
                    # Crear un diccionario para agrupar módulos por menú
                    menu_modules = {}
                    
                    # Recorrer los GroupModulePermission para obtener los módulos y permisos
                    for gmp in group_module_permissions:
                        module = gmp.module
                        menu = module.menu
                        
                        # Agregar permisos al conjunto global
                        for permission in gmp.permissions.all():
                            request.user_permissions.add(permission.codename)
                        
                        # Crear un diccionario con la información del módulo
                        module_info = {
                            'id': module.id,
                            'name': module.name,
                            'url': module.url,
                            'icon': module.icon,
                            'description': module.description,
                            'order': module.order,
                            'permissions': [p.codename for p in gmp.permissions.all()]
                        }
                        
                        # Agregar el módulo a la lista
                        request.user_modules.append(module_info)
                        
                        # Agrupar módulos por menú
                        if menu.id not in menu_modules:
                            menu_modules[menu.id] = {
                                'id': menu.id,
                                'name': menu.name,
                                'icon': menu.icon,
                                'order': menu.order,
                                'modules': []
                            }
                        
                        menu_modules[menu.id]['modules'].append(module_info)
                    
                    # Convertir el diccionario de menús a lista y ordenar
                    request.menu_list = sorted(menu_modules.values(), key=lambda x: x['order'])
                    
                    # Ordenar módulos dentro de cada menú
                    for menu_data in request.menu_list:
                        menu_data['modules'] = sorted(menu_data['modules'], key=lambda x: x['order'])
                
                except Group.DoesNotExist:
                    # Si el grupo no existe, eliminar de la sesión
                    if 'group_id' in request.session:
                        del request.session['group_id']
                    request.active_group = None
                    request.user_modules = []
                    request.user_permissions = set()
                    request.menu_list = []
            
            # Si no hay grupo activo en la sesión pero el usuario pertenece a grupos
            elif request.user.groups.exists():
                # Asignar el primer grupo como activo usando el método correcto
                from apps.security.components.group_session import UserGroupSession
                group_session = UserGroupSession(request)
                group = group_session.set_initial_group_session()
                # Procesar nuevamente con el grupo asignado
                return self.process_request(request)
            
            else:
                # Usuario sin grupos
                request.active_group = None
                request.user_modules = []
                request.user_permissions = set()
                request.menu_list = []
        
        except (ImportError, Exception) as e:
            # Si hay un error, inicializar valores por defecto
            request.active_group = None
            request.user_modules = []
            request.user_permissions = set()
            request.menu_list = []
        
        return None
