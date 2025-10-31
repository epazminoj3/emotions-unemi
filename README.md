
## ¿Qué hace el proyecto? Básicamente, el sistema puede:
- Detectar emociones vía webcam en tiempo real.
- Analizar emociones en las fotos cargadas.
- Muestra estadísticas sobre las emociones detectadas.
- Guardar el historial de todos los análisis.
- Administrar diferentes usuarios y sus permisos.

##Cómo lo construí
Elegí Django porque es confiable y me permite administrar bien los usuarios y los permisos. Para detectar emociones, implementé un sistema que procesa cada cuadro y reconoce expresiones faciales.
El proyecto se divide en dos partes principales:
1. Módulo de emoción: se encarga de todo lo relacionado con la detección.
2. Módulo de seguridad: se encarga de los usuarios y permisos.

## Instalar
Si quieres probar el proyecto, necesitas:
1. Clonar este repositorio
2. Instalar dependencias:
```
instalación de pip -r require.txt
```
3. Configuración de la base de datos:
```
Mover Python Managed.py
```
4. Inicie el servidor:
```
El servidor inicia Python Managed.py
```

## Estructura
```
emociones-unemi/
├── aplicaciones/
│ ├── emociones/ # Todos los códigos de detección
│ └── seguridad/ # Administrar usuarios y permisos
├── configuración/ # Ajustes generales
└── gestión.py
```

## Característica interesante
- Análisis en tiempo real súper fluido
- Interfaz fácil de usar
- Guardar el historial de todos los análisis.
- Sistema de usuario con diferentes niveles de acceso.
- Tabla de estadísticas

## Problemas comunes
- Si la cámara no funciona recuerda otorgar permisos al navegador
- El análisis funciona mejor en buenas condiciones de iluminación.
- No olvides instalar Python y sus dependencias.

## Planes para el futuro
Planeo agregar:
- Más tipos de emociones para detectar
- Exportar datos a Excel
- Modo nocturno
- Soporte en varios idiomas
