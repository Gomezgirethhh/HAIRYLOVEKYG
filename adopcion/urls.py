from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .viewsets import MascotaViewSet, AdopcionViewSet

# Router para APIs RESTful
router = DefaultRouter()
router.register(r'mascotas', MascotaViewSet, basename='mascota')
router.register(r'adopciones', AdopcionViewSet, basename='adopcion')

urlpatterns = [
    # Vistas tradicionales - Adopción
    path('mascotas/', views.mascotas, name='mascotas'),
    path('adoptar/', views.formulario_adopcion, name='formulario_adopcion'),
    path('descargar-reporte/<int:adopcion_id>/', views.descargar_reporte_adopcion, name='descargar_reporte_adopcion'),
    
    # Nuevas vistas para registrar mascotas en adopción
    path('registrar-mascota/', views.registrar_mascota_adopcion, name='registrar_mascota_adopcion'),
    path('mis-mascotas/', views.mis_mascotas_adopcion, name='mis_mascotas_adopcion'),
    path('disponibles/', views.mascotas_adopcion_disponibles, name='mascotas_adopcion_disponibles'),
    path('mascota/<int:mascota_id>/', views.detalles_mascota, name='detalles_mascota'),
    path('solicitar/<int:mascota_id>/', views.solicitar_adopcion, name='solicitar_adopcion'),
    path('mis-adopciones/', views.mis_adopciones, name='mis_adopciones'),
    
    # Vistas para que criadores manejen solicitudes de adopción
    path('solicitudes/', views.solicitudes_adopcion_criador, name='solicitudes_adopcion_criador'),
    path('solicitud/<int:adopcion_id>/aprobar/', views.aprobar_solicitud_adopcion, name='aprobar_solicitud_adopcion'),
    path('solicitud/<int:adopcion_id>/rechazar/', views.rechazar_solicitud_adopcion, name='rechazar_solicitud_adopcion'),
    
    # APIs RESTful
    path('api/', include(router.urls)),
]