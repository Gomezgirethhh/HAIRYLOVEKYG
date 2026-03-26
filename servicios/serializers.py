from rest_framework import serializers
from .models import Servicio
from usuarios.serializers import UsuarioSerializer


class ServicioSerializer(serializers.ModelSerializer):
    especialista = UsuarioSerializer(read_only=True)
    
    class Meta:
        model = Servicio
        fields = ['idServicio', 'nombre_servicio', 'descripcion', 
                  'precio_base', 'comision', 'especialista']
        read_only_fields = ['idServicio']
