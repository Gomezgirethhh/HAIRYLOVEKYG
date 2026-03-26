from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Mascota, Adopcion
from .serializers import (
    MascotaListSerializer, 
    MascotaDetailSerializer,
    AdopcionListSerializer, 
    AdopcionCreateSerializer
)

class MascotaViewSet(viewsets.ModelViewSet):
    """
    API para gestionar mascotas.
    Endpoints disponibles:
    - GET /api/mascotas/ - Listar todas las mascotas
    - GET /api/mascotas/?especie=Perro - Filtrar por especie
    - GET /api/mascotas/?raza=Labrador - Filtrar por raza
    - GET /api/mascotas/{id}/ - Obtener detalle de una mascota
    - POST /api/mascotas/ - Crear nueva mascota (requiere autenticación)
    - PUT/PATCH /api/mascotas/{id}/ - Actualizar mascota
    - DELETE /api/mascotas/{id}/ - Eliminar mascota
    - GET /api/mascotas/por_especie/ - Obtener especies disponibles
    """
    queryset = Mascota.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['Especie', 'Raza', 'Genero', 'Estado_Salud', 'Esterilizado', 'Socializado']
    search_fields = ['Nombre_Mascota', 'Raza', 'Especie', 'Color']
    ordering_fields = ['Nombre_Mascota', 'Peso', 'Fecha_Nacimiento']
    
    def get_serializer_class(self):
        """Usar diferentes serializadores según la acción"""
        if self.action == 'retrieve':
            return MascotaDetailSerializer
        elif self.action == 'list':
            return MascotaListSerializer
        return MascotaDetailSerializer
    
    @action(detail=False, methods=['get'])
    def por_especie(self, request):
        """Obtener todas las especies disponibles con conteo"""
        from django.db.models import Count
        especies = Mascota.objects.values('Especie').annotate(cantidad=Count('idMascota')).order_by('Especie')
        return Response(especies)
    
    @action(detail=False, methods=['get'])
    def razas_por_especie(self, request):
        """Obtener razas disponibles para una especie"""
        from .razas import RAZAS_POR_ESPECIE
        especie = request.query_params.get('especie', None)
        
        if especie:
            razas = RAZAS_POR_ESPECIE.get(especie, [])
            return Response({'especie': especie, 'razas': razas})
        
        return Response(RAZAS_POR_ESPECIE)
    
    @action(detail=False, methods=['get'])
    def disponibles(self, request):
        """Obtener solo mascotas disponibles para adopción"""
        mascotas = self.filter_queryset(self.get_queryset())
        # Excluir mascotas que ya fueron adoptadas
        adoptadas = Adopcion.objects.filter(Estado='Aprobada').values_list('idMascota', flat=True)
        disponibles = mascotas.exclude(idMascota__in=adoptadas)
        
        serializer = self.get_serializer(disponibles, many=True)
        return Response(serializer.data)


class AdopcionViewSet(viewsets.ModelViewSet):
    """
    API para gestionar adopciones.
    Endpoints disponibles:
    - GET /api/adopciones/ - Listar todas las adopciones
    - POST /api/adopciones/ - Crear nueva solicitud de adopción
    - GET /api/adopciones/{id}/ - Obtener detalle de adopción
    - PUT/PATCH /api/adopciones/{id}/ - Actualizar adopción
    - DELETE /api/adopciones/{id}/ - Eliminar adopción
    - GET /api/adopciones/mis-adopciones/ - Ver adopciones del usuario actual
    - GET /api/adopciones/pendientes/ - Ver adopciones pendientes (solo admin)
    """
    queryset = Adopcion.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['Estado', 'Estado_Solicitud', 'Fuente_Mascota']
    ordering_fields = ['Fecha_Solicitud', 'Fecha_Adopción']
    
    def get_serializer_class(self):
        """Usar diferentes serializadores según la acción"""
        if self.action == 'create':
            return AdopcionCreateSerializer
        return AdopcionListSerializer
    
    def create(self, request, *args, **kwargs):
        """Crear nueva solicitud de adopción"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def mis_adopciones(self, request):
        """Obtener las adopciones del usuario actual"""
        # Asumir que idPropietario está relacionado con el usuario actual
        adopciones = self.filter_queryset(self.get_queryset()).filter(idPropietario=request.user.idUsuario)
        serializer = self.get_serializer(adopciones, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def pendientes(self, request):
        """Obtener adopciones pendientes (solo administradores)"""
        pendientes = self.filter_queryset(self.get_queryset()).filter(Estado='Pendiente')
        serializer = self.get_serializer(pendientes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def aprobar(self, request, pk=None):
        """Aprobar una solicitud de adopción (solo admin)"""
        if not request.user.is_staff:
            return Response({'error': 'No tienes permisos para aprobar adopciones'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        adopcion = self.get_object()
        adopcion.Estado = 'Aprobada'
        adopcion.Estado_Solicitud = 'Completada'
        adopcion.save()
        
        serializer = self.get_serializer(adopcion)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def rechazar(self, request, pk=None):
        """Rechazar una solicitud de adopción (solo admin)"""
        if not request.user.is_staff:
            return Response({'error': 'No tienes permisos para rechazar adopciones'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        adopcion = self.get_object()
        adopcion.Estado = 'Rechazada'
        adopcion.Estado_Solicitud = 'Cancelada'
        adopcion.save()
        
        serializer = self.get_serializer(adopcion)
        return Response(serializer.data)
