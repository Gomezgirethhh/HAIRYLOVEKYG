from rest_framework.routers import DefaultRouter
from usuarios.views import UsuarioViewSet, PropietarioViewSet, CriadorViewSet, EspecialistaViewSet
from servicios.views import ServicioViewSet
from adopcion.views import MascotaViewSet, AdopcionViewSet

# Crear router
router = DefaultRouter()

# Registrar viewsets de usuarios
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'propietarios', PropietarioViewSet, basename='propietario')
router.register(r'criadores', CriadorViewSet, basename='criador')
router.register(r'especialistas', EspecialistaViewSet, basename='especialista')

# Registrar viewsets de servicios
router.register(r'servicios', ServicioViewSet, basename='servicio')

# Registrar viewsets de adopción
router.register(r'mascotas', MascotaViewSet, basename='mascota')
router.register(r'adopciones', AdopcionViewSet, basename='adopcion')

urlpatterns = router.urls
