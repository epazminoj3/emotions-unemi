
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
1. Clonar este repositorio en ``cmd``
```
git clone https://github.com/epazminoj3/emotions-unemi.git
```
2. Crea un entorno virtual
``` 
cd emotions-unemi
```
```
python -m venv venv
```
```
cd venv/scripts
```
```
activate
```
Recuerda volver a la carpeta principal ``emotions-unemi``, ejecuta 2 veces:
```
cd ..
```
3. Instalar dependencias:
```
pip install -r requirements.txt
```
3. Configura la base de datos en el archivo ``.env``:
- DB_NAME=emotions    #Cambiala por tu base de datos
- DB_USER=postgres
- DB_PASSWORD=1234    #Cambiala segun tu base de datos
- DB_HOST=localhost
- DB_PORT=5432
- no olvide guardar los cambios.
5. Ejecuta las migraciones:
```
python manage.py makemigrations
```
```
python manage.py migrate
```
6. Ya casi terminamos, para iniciar rapido ejecute un scripts inicial:
```
python script_inicial.py
```
. El scripts le dira el ``superusuario`` y configurara el sistema:
- Email:
```
admin@gmail.com
```
- Contraseña
```
admin
```
5. Inicie el servidor:
```
python manage.py runserver
```

## Estructura
```
emociones-unemi/
├── apps/
│ ├── emotions/ # Todos los códigos de detección
│ └── security/ # Administrar usuarios y permisos
├── config/ # Ajustes generales
└── manage.py
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
