from apps.security.components.group_permission import GroupPermission
from apps.security.models import GroupModulePermission
from apps.security.models import SystemConfig
from django.urls import reverse

def global_user_context(request):
    context = {}
    user = getattr(request, 'user', None)
    if user and user.is_authenticated:
        user_groups = user.groups.all()
        active_group = None
        # Buscar el grupo activo en la sesión
        if 'group_id' in request.session:
            try:
                active_group = user_groups.get(id=request.session['group_id'])
            except Exception:
                active_group = user_groups.first() if user_groups.exists() else None
                if active_group:
                    request.session['group_id'] = active_group.id
        else:
            active_group = user_groups.first() if user_groups.exists() else None
            if active_group:
                request.session['group_id'] = active_group.id

        context['active_group'] = active_group
        context['user_groups'] = user_groups

        # Menús y módulos agrupados por menú
        menu_list = []
        if active_group:
            group_module_permissions = GroupModulePermission.objects.filter(
                group=active_group,
                module__is_active=True
            ).select_related('module', 'module__menu').order_by('module__menu__order', 'module__order')
            menus_processed = {}
            for gmp in group_module_permissions:
                menu = gmp.module.menu
                if menu.id not in menus_processed:
                    menu_item = {
                        'menu': menu,
                        'group_module_permission_list': []
                    }
                    menus_processed[menu.id] = len(menu_list)
                    menu_list.append(menu_item)
                menu_index = menus_processed[menu.id]
                menu_list[menu_index]['group_module_permission_list'].append(gmp)
        context['menu_list'] = menu_list

        # Permisos del grupo activo
        context['permissions'] = GroupPermission.get_permission_dict_of_group(user, active_group)

        # Módulos permitidos para el buscador
        allowed_modules = []
        if active_group:
            group_modules = GroupModulePermission.objects.get_group_module_permission_active_list(active_group.id)
            for gmp in group_modules:
                module = gmp.module
                if module.is_active:
                    module_url = reverse('dashboard') if module.url == 'dashboard/' else f'/{module.url}'
                    allowed_modules.append({
                        'name': module.name,
                        'icon': module.icon,
                        'url': module_url,
                        'description': module.description or f'Módulo de {module.name}'
                    })
        context['modules'] = allowed_modules
    return context


def system_config_context(request):
    """
    Contexto global para información del sistema desde SystemConfig.
    """
    try:
        config = SystemConfig.objects.first()
        return {
            'SYSTEM_NAME': config.name if config else 'Mi Sistema',
            'SYSTEM_DESCRIPTION': config.description if config else '',
            'SYSTEM_ICON': config.icon if config else 'fas fa-bolt',
            'SYSTEM_LOGO': config.logo.url if config and config.logo else None,
            'SYSTEM_COMPANY': config.company if config else 'Mi Sistema',
            'SYSTEM_YEAR': config.year if config else 2025,
        }
    except:
        # Si hay error o no hay configuración, valores por defecto
        return {
            'SYSTEM_NAME': 'Mi Sistema',
            'SYSTEM_DESCRIPTION': 'Plataforma innovadora para la gestión integral de proyectos.',
            'SYSTEM_ICON': 'fas fa-bolt',
            'SYSTEM_LOGO': None,
            'SYSTEM_COMPANY': 'Mi Sistema',
            'SYSTEM_YEAR': 2025,
        }