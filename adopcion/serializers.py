from rest_framework import serializers
from .models import Mascota, Adopcion
from django.utils.timezone import now


class MascotaListSerializer(serializers.ModelSerializer):
    """Serializador simple para listados de mascotas"""
    class Meta:
        model = Mascota
        fields = ['idMascota', 'Nombre_Mascota', 'Especie', 'Raza', 'Genero', 'Peso', 'Estado_Salud', 'Esterilizado', 'Socializado']

class MascotaDetailSerializer(serializers.ModelSerializer):
    """Serializador detallado para mascotas"""
    class Meta:
        model = Mascota
        fields = '__all__'

class AdopcionListSerializer(serializers.ModelSerializer):
    """Serializador para listados de adopciones"""
    mascota_info = MascotaListSerializer(source='idMascota', read_only=True)
    
    class Meta:
        model = Adopcion
        fields = ['idAdopcion', 'idPropietario', 'idMascota', 'mascota_info', 'Estado', 
                  'Fecha_Solicitud', 'Fecha_Adopción', 'Motivo_Adopción', 'Estado_Solicitud']

class AdopcionCreateSerializer(serializers.ModelSerializer):
    """Serializador para crear adopciones"""
    class Meta:
        model = Adopcion
        fields = ['idMascota', 'idPropietario', 'Motivo_Adopción', 'Lugar_Vivienda', 
                  'Fecha_Adopción', 'Fecha_Entrega', 'Info_Mascota', 'Estado_Salud_Mascota']

    def create(self, validated_data):
        validated_data['Estado'] = 'Pendiente'
        validated_data['Fecha_Solicitud'] = now().date()
        validated_data['Estado_Solicitud'] = 'En revisión'
        validated_data['Estado_Ingreso_Mascota'] = ''
        validated_data['Control_Adopción'] = ''
        validated_data['Devolución'] = ''
        return super().create(validated_data)

# Mantener compatibilidad con código antiguo
class MascotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mascota
        fields = ['idMascota', 'Nombre_Mascota', 'Fecha_Nacimiento', 
                  'Raza', 'Genero', 'Peso', 'Especie', 'Color', 
                  'Tamaño', 'Origen', 'Tipo_Alimentación', 'Vacunas', 
                  'Esterilizado', 'Socializado', 'Estado_Salud']
        read_only_fields = ['idMascota']


class AdopcionSerializer(serializers.ModelSerializer):
    idMascota = MascotaSerializer(read_only=True)
    
    class Meta:
        model = Adopcion
        fields = ['idAdopcion', 'idPropietario', 'idMascota', 'idCriador',
                  'Estado', 'Fecha_Solicitud', 'Fecha_Adopción', 
                  'Motivo_Adopción', 'Estado_Solicitud', 'Fuente_Mascota']
        read_only_fields = ['idAdopcion', 'idMascota']
