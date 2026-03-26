"""
Utilidades avanzadas para filtros, búsquedas y consultas en la API
"""

import django_filters
from .models import Mascota, Adopcion


class MascotaFilter(django_filters.FilterSet):
    """Filtros avanzados para el modelo Mascota"""
    
    # Filtros de rango de peso
    peso_minimo = django_filters.NumberFilter(
        field_name='Peso',
        lookup_expr='gte',
        label='Peso mínimo'
    )
    peso_maximo = django_filters.NumberFilter(
        field_name='Peso',
        lookup_expr='lte',
        label='Peso máximo'
    )
    
    # Filtros de fechas
    fecha_nacimiento_desde = django_filters.DateFilter(
        field_name='Fecha_Nacimiento',
        lookup_expr='gte',
        label='Fecha de nacimiento desde'
    )
    fecha_nacimiento_hasta = django_filters.DateFilter(
        field_name='Fecha_Nacimiento',
        lookup_expr='lte',
        label='Fecha de nacimiento hasta'
    )
    
    # Búsqueda por nombre, raza o color
    busqueda = django_filters.CharFilter(
        method='filtrar_busqueda',
        label='Buscar por nombre, raza o color'
    )
    
    # Filtro por compatibilidad
    compatible_mascotas = django_filters.CharFilter(
        field_name='Compatibilidad_Mascota',
        lookup_expr='icontains',
        label='Compatible con mascotas'
    )
    
    class Meta:
        model = Mascota
        fields = {
            'Especie': ['exact'],
            'Raza': ['exact'],
            'Genero': ['exact'],
            'Estado_Salud': ['exact'],
            'Esterilizado': ['exact'],
            'Socializado': ['exact'],
            'Tamaño': ['exact'],
        }
    
    def filtrar_busqueda(self, queryset, name, value):
        """Búsqueda en múltiples campos"""
        return queryset.filter(
            models.Q(Nombre_Mascota__icontains=value) |
            models.Q(Raza__icontains=value) |
            models.Q(Color__icontains=value)
        )


class AdopcionFilter(django_filters.FilterSet):
    """Filtros avanzados para el modelo Adopcion"""
    
    fecha_solicitud_desde = django_filters.DateFilter(
        field_name='Fecha_Solicitud',
        lookup_expr='gte',
        label='Fecha solicitud desde'
    )
    fecha_solicitud_hasta = django_filters.DateFilter(
        field_name='Fecha_Solicitud',
        lookup_expr='lte',
        label='Fecha solicitud hasta'
    )
    
    class Meta:
        model = Adopcion
        fields = {
            'Estado': ['exact'],
            'Estado_Solicitud': ['exact'],
            'Fuente_Mascota': ['exact'],
        }


# Importar Q para búsquedas complejas
from django.db.models import Q
