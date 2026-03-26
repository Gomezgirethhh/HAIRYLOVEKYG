from django.shortcuts import render
from rest_framework import viewsets, permissions, pagination
from .models import Servicio
from .serializers import ServicioSerializer


# ==================== VISTAS TRADICIONALES ====================

def lista_servicios(request):
    """Página de lista de servicios disponibles."""
    servicios = Servicio.objects.all()
    return render(request, 'servicios/lista_servicios.html', {'servicios': servicios})


def servicios(request):
    servicios = Servicio.objects.all()
    return render(request, 'servicios/servicios.html', {'servicios': servicios})


# ==================== API VIEWSETS ====================

class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


class ServicioViewSet(viewsets.ModelViewSet):
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_fields = ['especialista']
    search_fields = ['nombre_servicio', 'descripcion']
    ordering_fields = ['precio_base']
    ordering = ['precio_base']
