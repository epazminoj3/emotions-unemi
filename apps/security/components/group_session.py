from django.contrib.auth.models import Group

class UserGroupSession: 
    def __init__(self, request):
        self.request = request

    def get_group_session(self):
        """Obtiene el grupo activo de la sesión"""
        if 'group_id' in self.request.session:
            try:
                return Group.objects.get(pk=self.request.session['group_id'])
            except Group.DoesNotExist:
                # Si el grupo no existe, eliminar de la sesión
                del self.request.session['group_id']
                return None
        return None

    def set_initial_group_session(self):
        """Establece el grupo inicial en la sesión si no existe"""
        if 'group_id' not in self.request.session:
            groups = self.request.user.groups.all().order_by('id')
            if groups.exists():
                # Lógica mejorada para seleccionar el grupo por defecto
                default_group = self._get_default_group(groups)
                self.request.session['group_id'] = default_group.id
                return default_group
            else:
                # Si el usuario no tiene grupos, no hacer nada y devolver None
                # Esto evita errores cuando se intenta acceder a permisos
                return None
        return self.get_group_session()
    
    def _get_default_group(self, groups):
        """
        Selecciona el grupo por defecto basado en prioridades:
        1. Grupo con menos permisos (más restrictivo)
        2. Grupo que no sea "Administrador" si hay otros disponibles
        3. Primer grupo por ID (fallback)
        """
        # Convertir a lista para múltiples evaluaciones
        group_list = list(groups)
        
        # Si solo hay un grupo, usarlo
        if len(group_list) == 1:
            return group_list[0]
        
        # Buscar un grupo que no sea "Administrador" primero
        non_admin_groups = [g for g in group_list if g.name.lower() != 'administrador']
        if non_admin_groups:
            # De los grupos no-admin, tomar el primero por ID
            return min(non_admin_groups, key=lambda g: g.id)
        
        # Si todos son admin o no hay preferencia, usar el primero
        return group_list[0]

    @staticmethod
    def set_group_session(request, group_id):
        """Establece un grupo específico en la sesión"""
        try:
            group = Group.objects.get(pk=group_id)
            # Verificar que el usuario pertenezca al grupo
            if group in request.user.groups.all():
                request.session['group_id'] = int(group_id)
                # Forzar el guardado de la sesión solo si tiene el atributo modified
                if hasattr(request.session, 'modified'):
                    request.session.modified = True
                return True
            return False
        except Group.DoesNotExist:
            return False
        except Exception as e:
            print(f"Error en set_group_session: {e}")
            return False

    @staticmethod
    def clear_group_session(request):
        """Limpia el grupo de la sesión"""
        if 'group_id' in request.session:
            del request.session['group_id']
            if hasattr(request.session, 'modified'):
                request.session.modified = True

    def get_user_groups(self):
        """Obtiene todos los grupos del usuario"""
        return self.request.user.groups.all().order_by('name')

    def has_group(self, group_name):
        """Verifica si el usuario pertenece a un grupo específico"""
        return self.request.user.groups.filter(name=group_name).exists()

    def get_active_group_permissions(self):
        """Obtiene los permisos del grupo activo"""
        active_group = self.get_group_session()
        if active_group:
            return active_group.permissions.all()
        return []

    def set_group_session_instance(self):
        """Método de instancia para establecer el grupo inicial en la sesión"""
        return self.set_initial_group_session()

    def set_current_group(self, group_id):
        """Método de instancia para cambiar el grupo actual"""
        return self.set_group_session(self.request, group_id)

