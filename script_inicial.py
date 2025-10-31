#!/usr/bin/env python
"""
Script de inicialización rápida del sistema
Crea los datos iniciales: grupos, superuser, menús, módulos y permisos
Ejecutar con: python setup_initial_data.py
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.security.models import User, Menu, Module, GroupModulePermission, SystemConfig
from django.db import transaction

def create_initial_data():
    """Crea todos los datos iniciales del sistema"""
    
    print("=" * 70)
    print("🚀 INICIANDO CONFIGURACIÓN DEL SISTEMA")
    print("=" * 70)
    
    with transaction.atomic():
        
        # 1. CREAR CONFIGURACIÓN DEL SISTEMA
        print("\n📋 1. Configurando información del sistema...")
        system_config, created = SystemConfig.objects.get_or_create(
            id=1,
            defaults={
                'name': 'Sistema de Detección de Emociones',
                'description': 'Plataforma innovadora para la gestión y análisis de emociones mediante inteligencia artificial.',
                'icon': 'fas fa-brain',
                'company': 'Emotion Tech',
                'year': 2025
            }
        )
        if created:
            print("   ✅ Configuración del sistema creada")
        else:
            print("   ℹ️  Configuración del sistema ya existe")
        
        # 2. CREAR GRUPO ADMINISTRADOR
        print("\n👥 2. Creando grupo Administrador...")
        grupo_admin, created = Group.objects.get_or_create(name='Administrador')
        if created:
            print("   ✅ Grupo 'Administrador' creado")
        else:
            print("   ℹ️  Grupo 'Administrador' ya existe")
        
        # 3. CREAR SUPERUSUARIO
        print("\n👤 3. Creando superusuario...")
        email = 'admin@emotions.com'
        username = 'admin'
        
        if not User.objects.filter(email=email).exists():
            superuser = User.objects.create_superuser(
                username=username,
                email=email,
                password='admin123',  # CAMBIAR EN PRODUCCIÓN
                first_name='Super',
                last_name='Administrador',
                dni='0000000000',
                direction='Oficina Central',
                phone='0999999999'
            )
            superuser.groups.add(grupo_admin)
            print(f"   ✅ Superusuario creado:")
            print(f"      - Email: {email}")
            print(f"      - Password: admin123")
            print(f"      - Grupo: Administrador")
        else:
            superuser = User.objects.get(email=email)
            superuser.groups.add(grupo_admin)
            print(f"   ℹ️  Superusuario ya existe: {email}")
        
        # 4. CREAR MENÚS
        print("\n📑 4. Creando menús...")
        menus_data = [
            {'name': 'Seguridad', 'icon': 'fas fa-key', 'order': 1},
            {'name': 'Emotions', 'icon': 'fas fa-smile', 'order': 2},
        ]
        
        menus = {}
        for menu_data in menus_data:
            menu, created = Menu.objects.get_or_create(
                name=menu_data['name'],
                defaults={
                    'icon': menu_data['icon'],
                    'order': menu_data['order']
                }
            )
            menus[menu_data['name']] = menu
            status = "✅ Creado" if created else "ℹ️  Ya existe"
            print(f"   {status}: {menu.name} ({menu.icon})")
        
        # 5. CREAR MÓDULOS
        print("\n📦 5. Creando módulos...")
        modulos_data = [
            # Módulos de Seguridad
            {
                'name': 'Info System',
                'url': 'security/system-config/',
                'menu': 'Seguridad',
                'icon': 'fas fa-cog',
                'order': 0,
                'description': 'Configuración general del sistema'
            },
            {
                'name': 'Gestion de usuarios',
                'url': 'security/users/',
                'menu': 'Seguridad',
                'icon': 'fas fa-users',
                'order': 1,
                'description': 'Administración de usuarios del sistema'
            },
            {
                'name': 'Gestion de menus',
                'url': 'security/menus/',
                'menu': 'Seguridad',
                'icon': 'fas fa-bars',
                'order': 2,
                'description': 'Configuración de menús de navegación'
            },
            {
                'name': 'Gestion de grupos',
                'url': 'security/groups/',
                'menu': 'Seguridad',
                'icon': 'fas fa-users-cog',
                'order': 3,
                'description': 'Administración de grupos de usuarios'
            },
            {
                'name': 'Gestion de modulos',
                'url': 'security/modules/',
                'menu': 'Seguridad',
                'icon': 'fas fa-th-large',
                'order': 4,
                'description': 'Configuración de módulos del sistema'
            },
            {
                'name': 'Gestion de permisos',
                'url': 'security/group-module-permissions/',
                'menu': 'Seguridad',
                'icon': 'fas fa-shield-alt',
                'order': 5,
                'description': 'Asignación de permisos a grupos'
            },
            # Módulos de Emotions
            {
                'name': 'Deteccion en tiempo real',
                'url': 'emotions/real-time/',
                'menu': 'Emotions',
                'icon': 'fas fa-video',
                'order': 0,
                'description': 'Detección de emociones en tiempo real'
            },
            {
                'name': 'Deteccion de emociones por camara',
                'url': 'emotions/camera/',
                'menu': 'Emotions',
                'icon': 'fas fa-camera',
                'order': 1,
                'description': 'Captura y análisis mediante cámara'
            },
            {
                'name': 'Detector de emociones',
                'url': 'emotions/',
                'menu': 'Emotions',
                'icon': 'fas fa-smile-beam',
                'order': 2,
                'description': 'Panel principal de detección'
            },
            {
                'name': 'Deteccion de emociones rapida',
                'url': 'emotions/quick/',
                'menu': 'Emotions',
                'icon': 'fas fa-bolt',
                'order': 3,
                'description': 'Análisis rápido de emociones'
            },
            {
                'name': 'Analisis de emociones',
                'url': 'emotions/analysis/',
                'menu': 'Emotions',
                'icon': 'fas fa-chart-line',
                'order': 4,
                'description': 'Estadísticas y análisis detallado'
            },
        ]
        
        modulos = []
        for modulo_data in modulos_data:
            menu = menus[modulo_data['menu']]
            modulo, created = Module.objects.get_or_create(
                url=modulo_data['url'],
                defaults={
                    'name': modulo_data['name'],
                    'menu': menu,
                    'icon': modulo_data['icon'],
                    'order': modulo_data['order'],
                    'description': modulo_data['description'],
                    'is_active': True
                }
            )
            modulos.append(modulo)
            status = "✅ Creado" if created else "ℹ️  Ya existe"
            print(f"   {status}: {modulo.name} [{modulo.url}]")
        
        # 6. OBTENER PERMISOS Y CREAR GRUPO-MÓDULO-PERMISOS
        print("\n🔐 6. Configurando permisos del grupo Administrador...")
        
        # Obtener todos los permisos de los modelos relevantes
        content_types = ContentType.objects.filter(
            app_label__in=['security', 'emotions']
        )
        all_permissions = Permission.objects.filter(content_type__in=content_types)
        
        print(f"   📊 Total de permisos disponibles: {all_permissions.count()}")
        
        # Asignar todos los módulos al grupo Administrador con todos sus permisos
        for modulo in modulos:
            gmp, created = GroupModulePermission.objects.get_or_create(
                group=grupo_admin,
                module=modulo
            )
            
            # Asignar todos los permisos disponibles
            gmp.permissions.set(all_permissions)
            
            status = "✅ Configurado" if created else "🔄 Actualizado"
            print(f"   {status}: {modulo.name} - {all_permissions.count()} permisos asignados")
        
    print("\n" + "=" * 70)
    print("✨ ¡CONFIGURACIÓN COMPLETADA EXITOSAMENTE!")
    print("=" * 70)
    print("\n📝 CREDENCIALES DE ACCESO:")
    print(f"   Email:    admin@emotions.com")
    print(f"   Password: admin123")
    print(f"   Grupo:    Administrador")
    print("\n⚠️  IMPORTANTE: Cambia la contraseña en producción")
    print("=" * 70)

if __name__ == '__main__':
    try:
        create_initial_data()
    except Exception as e:
        print("\n❌ ERROR durante la configuración:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
