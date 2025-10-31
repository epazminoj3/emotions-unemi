from django.db.models import Q

#
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils.decorators import method_decorator

from apps.security.components.group_permission import GroupPermission
from apps.security.components.group_session import UserGroupSession
from apps.security.components.menu_module import MenuModule

# configuracion de contexto generico y permisos de botones
class ListViewMixin(object):
    query = None
    paginate_by = 8
  
    
    def dispatch(self, request, *args, **kwargs):
        self.query = Q()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'{self.model._meta.verbose_name_plural}'
        context['title1'] = f'Consulta de {self.model._meta.verbose_name_plural}'
        # añade los permisos del grupo activo(add_pais, view_ciudad)
        # print("estoy en el mixing..")
        # print(self.request.session.get('group_id'))
        MenuModule(self.request).fill(context)
        userGroupSession=UserGroupSession(self.request)
        group = userGroupSession.get_group_session()
        context['permissions'] = GroupPermission.get_permission_dict_of_group(self.request.user,group)
        # crear la data y la session con los menus y modulos del usuario 
        return context

   

class CreateViewMixin(object):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'{self.model._meta.verbose_name}'
        context['title1'] = f'Ingresar {self.model._meta.verbose_name_plural}'
        MenuModule(self.request).fill(context)
        userGroupSession=UserGroupSession(self.request)
        group = userGroupSession.get_group_session()
        context['permissions'] = GroupPermission.get_permission_dict_of_group(self.request.user,group)
        return context                     


class UpdateViewMixin(object):
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'{self.model._meta.verbose_name_plural}'
        context['title1'] = f'Ingresar {self.model._meta.verbose_name_plural}'
        MenuModule(self.request).fill(context)
        userGroupSession=UserGroupSession(self.request)
        group = userGroupSession.get_group_session()
        context['permissions'] = GroupPermission.get_permission_dict_of_group(self.request.user,group)
        return context

class DetailViewMixin(object):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'{self.model._meta.verbose_name}'
        context['title1'] = f'Detalle de {self.model._meta.verbose_name}'
        MenuModule(self.request).fill(context)
        userGroupSession = UserGroupSession(self.request)
        group = userGroupSession.get_group_session()
        context['permissions'] = GroupPermission.get_permission_dict_of_group(self.request.user, group)
        return context
     
class DeleteViewMixin(object):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print("entro al deleteMixin")
        context['title'] = f'{self.model._meta.verbose_name_plural}'
        MenuModule(self.request).fill(context)
        userGroupSession=UserGroupSession(self.request)
        group = userGroupSession.get_group_session()
        context['permissions'] = GroupPermission.get_permission_dict_of_group(self.request.user,group)
        return context

      
         
# Permisos de urls o modulos
class PermissionMixin(object):
    permission_required = ''
    
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            user_session = UserGroupSession(request)
            user_session.set_group_session_instance()

            if 'group_id' not in request.session:
                messages.error(request, 'No hay grupo seleccionado. Redirigiendo a login.')
                return redirect('security:signin')

            if user.is_superuser:
                # Los superusuarios siempre tienen acceso
                return super().get(request, *args, **kwargs)

            group = user_session.get_group_session()
            permissions = self._get_permissions_to_validate()
            
            # Debug: agregar logging para entender qué está pasando
            from apps.security.components.group_permission import GroupPermission
            GroupPermission.debug_user_permissions(user, group, request.path)
            
            # Si no hay permisos que validar, permitir acceso
            if not permissions:
                return super().get(request, *args, **kwargs)

            # Verificar si el grupo tiene los permisos requeridos
            has_perm = False
            try:
                # Obtener el módulo actual basado en la URL
                from apps.security.models import Module
                current_path = request.path
                current_module = None
                
                # Buscar el módulo que corresponde a la URL actual
                for module in Module.objects.filter(is_active=True):
                    if module.url and module.url in current_path:
                        current_module = module
                        break
                
                print(f"=== DEBUG PERMISOS ===")
                print(f"Usuario: {user.username}")
                print(f"Grupo: {group.name}")
                print(f"URL actual: {current_path}")
                print(f"Módulo encontrado: {current_module}")
                print(f"Permisos requeridos: {permissions}")
                
                if current_module:
                    # Verificar si el grupo tiene permisos para este módulo específico
                    group_module_perm = group.module_permissions.filter(module=current_module).first()
                    if group_module_perm:
                        # Verificar si los permisos requeridos están en los permisos del grupo para este módulo
                        group_permissions = list(group_module_perm.permissions.values_list('codename', flat=True))
                        print(f"Permisos del grupo para este módulo: {group_permissions}")
                        
                        # Verificar TODOS los permisos requeridos (no solo uno)
                        for perm in permissions:
                            if perm in group_permissions:
                                has_perm = True
                                print(f"✓ Permiso encontrado: {perm}")
                            else:
                                print(f"✗ Permiso NO encontrado: {perm}")
                                has_perm = False
                                break  # Si falta un permiso, no tiene acceso
                    else:
                        print(f"✗ No hay permisos asignados para este módulo")
                        has_perm = False
                else:
                    print(f"✗ No se encontró módulo para la URL: {current_path}")
                    has_perm = False
                
                print(f"Resultado final: {has_perm}")
                
                if not has_perm:
                    print(f"ACCESO DENEGADO: Usuario {user.username} en grupo {group.name}")
                    messages.error(request, f'No tiene permisos para realizar esta acción. Se requiere: {", ".join(permissions)}')
                    return redirect('security:dashboard')
                
            except Exception as perm_ex:
                print(f"Error verificando permisos: {perm_ex}")
                messages.error(request, f'Error verificando permisos: {perm_ex}')
                return redirect('security:dashboard')

            return super().get(request, *args, **kwargs)

        except Exception as ex:
            messages.error(
                request,
                'A ocurrido un error al ingresar al modulo, error para el admin es : {}'.format(ex))

        if request.user.is_authenticated:
            return redirect('security:dashboard')

        return redirect('security:signin')

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        """Validar permisos también para métodos POST"""
        try:
            user = request.user
            user_session = UserGroupSession(request)
            user_session.set_group_session_instance()

            if 'group_id' not in request.session:
                messages.error(request, 'No hay grupo seleccionado. Redirigiendo a login.')
                return redirect('security:signin')

            if user.is_superuser:
                # Los superusuarios siempre tienen acceso
                return super().post(request, *args, **kwargs)

            group = user_session.get_group_session()
            permissions = self._get_permissions_to_validate()
            
            print(f"=== DEBUG PERMISOS POST ===")
            print(f"Usuario: {user.username}")
            print(f"Grupo: {group.name}")
            print(f"URL actual: {request.path}")
            print(f"Permisos requeridos: {permissions}")
            
            # Si no hay permisos que validar, permitir acceso
            if not permissions:
                return super().post(request, *args, **kwargs)

            # Verificar permisos (mismo código que en GET)
            has_perm = False
            try:
                from apps.security.models import Module
                current_path = request.path
                current_module = None
                
                # Buscar el módulo que corresponde a la URL actual
                for module in Module.objects.filter(is_active=True):
                    if module.url and module.url in current_path:
                        current_module = module
                        break
                
                if current_module:
                    # Verificar si el grupo tiene permisos para este módulo específico
                    group_module_perm = group.module_permissions.filter(module=current_module).first()
                    if group_module_perm:
                        # Verificar si los permisos requeridos están en los permisos del grupo para este módulo
                        group_permissions = list(group_module_perm.permissions.values_list('codename', flat=True))
                        print(f"Permisos del grupo para este módulo: {group_permissions}")
                        
                        # Verificar TODOS los permisos requeridos
                        for perm in permissions:
                            if perm in group_permissions:
                                has_perm = True
                                print(f"✓ Permiso encontrado: {perm}")
                            else:
                                print(f"✗ Permiso NO encontrado: {perm}")
                                has_perm = False
                                break
                    else:
                        print(f"✗ No hay permisos asignados para este módulo")
                        has_perm = False
                else:
                    print(f"✗ No se encontró módulo para la URL: {current_path}")
                    has_perm = False
                
                print(f"Resultado final POST: {has_perm}")
                
                if not has_perm:
                    print(f"POST DENEGADO: Usuario {user.username} en grupo {group.name}")
                    messages.error(request, f'No tiene permisos para realizar esta acción. Se requiere: {", ".join(permissions)}')
                    return redirect('security:dashboard')
                
            except Exception as perm_ex:
                print(f"Error verificando permisos en POST: {perm_ex}")
                messages.error(request, f'Error verificando permisos: {perm_ex}')
                return redirect('security:dashboard')

            return super().post(request, *args, **kwargs)

        except Exception as ex:
            messages.error(
                request,
                'A ocurrido un error al procesar la acción, error para el admin es : {}'.format(ex))
            return redirect('security:dashboard')

    def _get_permissions_to_validate(self):

        if self.permission_required == '':
            return ()

        if isinstance(self.permission_required, str):
            return self.permission_required, 

        return tuple(self.permission_required)
