"""
Configuración de URLs para el proyecto config.

La lista `urlpatterns` enruta URLs a vistas. Para más información, consulta:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Ejemplos:
Vistas basadas en funciones
    1. Agrega una importación:  from my_app import views
    2. Agrega una URL a urlpatterns:  path('', views.home, name='home')
Vistas basadas en clases
    1. Agrega una importación:  from other_app.views import Home
    2. Agrega una URL a urlpatterns:  path('', Home.as_view(), name='home')
Incluyendo otro URLconf
    1. Importa la función include(): from django.urls import include, path
    2. Agrega una URL a urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from apps.security.views.auth import signin, signout

urlpatterns = [
    path('admin/', admin.site.urls),

    path("", signin, name="signin"),
    path("signin/", signin, name="signin"),
    path("signout/", signout, name="signout"),
    
    path('security/', include(('apps.security.urls', 'security'), namespace='security')),
    path('emotions/', include(('apps.emotions.urls', 'emotions'), namespace='emotions')),
]

if settings.DEBUG:
    # Include django_browser_reload URLs solo en modo DEBUG 
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]
    # Servir archivos media en desarrollo
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
