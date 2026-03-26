"""
URL configuration for hairylove project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Documentación Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="HAIRY LOVE API",
        default_version='v1',
        description="API para gestión de adopción de mascotas",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="hairylove@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Vistas tradicionales
    path('', include('usuarios.urls')),
    path('servicios/', include('servicios.urls')),
    path('adopcion/', include('adopcion.urls')),
    
    # API REST
    path('api/', include('hairylove.api_urls')),
    path('api/auth/', include('rest_framework.urls')),
    
    # Documentación API
    path('api/docs/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/docs/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/docs/', schema_view.as_view(), name='schema-json'),
]

# Servir archivos de media (subidas de usuarios)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
