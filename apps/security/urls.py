"""

Vistas basadas en clases
1. Agrega una importación:  from other_app.views import Home
2. Agrega una URL a urlpatterns:  path('', Home.as_view(), name='home')

"""
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

#Importaciones de views
from apps.security.views.dashboard import DashboardView
from apps.security.views.auth import signin, signout
from apps.security.views.change_group import cambiar_grupo
from apps.security.views.signup import SignupView

# View de profile
from apps.security.views.profile import (
    UserProfileView,
    UserProfileUpdateView
)

# View de users
from apps.security.views.users import (
    UserListView,
    UserCreateView,
    UserUpdateView,
    UserDetailView,
    UserDeleteView
)

# View de menu
from apps.security.views.menu import (
    MenuListView,
    MenuCreateView,
    MenuUpdateView,
    MenuDetailView,
    MenuDeleteView
)

# View de system_config
from apps.security.views.system_config import (
    SystemConfigListView,
    SystemConfigCreateView,
    SystemConfigUpdateView,
    SystemConfigDetailView
)

# View de group
from apps.security.views.group import (
    GroupListView,
    GroupCreateView,
    GroupUpdateView,
    GroupDetailView,
    GroupDeleteView
)

# View de Module
from apps.security.views.module import (
    ModuleListView,
    ModuleCreateView,
    ModuleUpdateView,
    ModuleDetailView,
    ModuleDeleteView
)

from apps.security.views.permission import (
    GroupModulePermissionListView,
    GroupModulePermissionCreateView,
    GroupModulePermissionEditView,
    GroupModulePermissionDetailView,
    GroupModulePermissionDeleteView,
    module_permissions_ajax
)

# Vistas para restablecimiento de contraseña
from apps.security.views.password_reset import (
    CustomPasswordResetView,
    CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView
)

app_name="security"

urlpatterns = [
    path("dashboard_admin", DashboardView.as_view(), name="dashboard"),

    #Autenticación de usuario
    path('signin/', signin, name='signin'),
    path('signout/', signout, name='signout'),
    path('signup/', SignupView.as_view(), name='signup'),
    
    # Recuperación de contraseña
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    #Perfil de usuario
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/update/', UserProfileUpdateView.as_view(), name='profile_update'),

    #Cambio de grupo
    path('cambiar-grupo/', cambiar_grupo, name='cambiar_grupo'),

    # Usuarios
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/create/', UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/update/', UserUpdateView.as_view(), name='user_update'),
    path('users/<int:pk>/detail/', UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),
    
    # Menús
    path('menus/', MenuListView.as_view(), name='menu_list'),
    path('menus/create/', MenuCreateView.as_view(), name='menu_create'),
    path('menus/<int:pk>/update/', MenuUpdateView.as_view(), name='menu_update'),
    path('menus/<int:pk>/detail/', MenuDetailView.as_view(), name='menu_detail'),
    path('menus/<int:pk>/delete/', MenuDeleteView.as_view(), name='menu_delete'),

    # Configuración del Sistema
    path('system-config/', SystemConfigListView.as_view(), name='system_config_list'),
    path('system-config/create/', SystemConfigCreateView.as_view(), name='system_config_create'),
    path('system-config/<int:pk>/update/', SystemConfigUpdateView.as_view(), name='system_config_update'),
    path('system-config/<int:pk>/detail/', SystemConfigDetailView.as_view(), name='system_config_detail'),

    # Grupos
    path('groups/', GroupListView.as_view(), name='group_list'),
    path('groups/create/', GroupCreateView.as_view(), name='group_create'),
    path('groups/<int:pk>/update/', GroupUpdateView.as_view(), name='group_update'),
    path('groups/<int:pk>/detail/', GroupDetailView.as_view(), name='group_detail'),
    path('groups/<int:pk>/delete/', GroupDeleteView.as_view(), name='group_delete'),

    # Módulos
    path('modules/', ModuleListView.as_view(), name='module_list'),
    path('modules/create/', ModuleCreateView.as_view(), name='module_create'),
    path('modules/<int:pk>/update/', ModuleUpdateView.as_view(), name='module_update'),
    path('modules/<int:pk>/detail/', ModuleDetailView.as_view(), name='module_detail'),
    path('modules/<int:pk>/delete/', ModuleDeleteView.as_view(), name='module_delete'),

    # Permisos por Grupo/Módulo
    path('group-module-permissions/', GroupModulePermissionListView.as_view(), name='group_module_permission_list'),
    path('group-module-permissions/create/', GroupModulePermissionCreateView.as_view(), name='group_module_permission_create'),
    path('group-module-permissions/<int:pk>/edit/', GroupModulePermissionEditView.as_view(), name='group_module_permission_edit'),
    path('group-module-permissions/<int:pk>/detail/', GroupModulePermissionDetailView.as_view(), name='group_module_permission_detail'),
    path('group-module-permissions/<int:pk>/delete/', GroupModulePermissionDeleteView.as_view(), name='group_module_permission_delete'),
    # AJAX para permisos de módulo
    path('ajax/module-permissions/<int:module_id>/', module_permissions_ajax, name='ajax_module_permissions'),

    
]