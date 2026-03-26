from django import forms
from .models import Mascota, Adopcion
from django.utils import timezone


class MascotaAdopcionForm(forms.ModelForm):
    """Formulario para registrar una mascota en adopción"""
    
    class Meta:
        model = Mascota
        fields = [
            'Nombre_Mascota', 'Fecha_Nacimiento', 'Raza', 'Genero', 'Peso',
            'Especie', 'Color', 'Tamaño', 'Historial_Mascota', 'Tipo_Alimentación',
            'Enfermedades', 'Vivienda', 'Vacunas', 'Compatibilidad_Mascota',
            'Descripción_Física', 'Estado_Salud', 'Esterilizado', 'Socializado',
            'foto_mascota', 'Origen'
        ]
        widgets = {
            'Nombre_Mascota': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la mascota'
            }),
            'Fecha_Nacimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'Raza': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Labrador, Persa, etc.'
            }),
            'Genero': forms.Select(attrs={'class': 'form-control'}),
            'Peso': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Peso en kg',
                'step': '0.1'
            }),
            'Especie': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Perro, Gato, etc.'
            }),
            'Color': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Color o patrón de pelaje'
            }),
            'Tamaño': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Pequeño, Mediano, Grande, Muy Grande'
            }),
            'Historial_Mascota': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Historias, eventos destacables...'
            }),
            'Tipo_Alimentación': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Croquetas, dieta especial, etc.'
            }),
            'Enfermedades': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enfermedades previas, alergias, condiciones...'
            }),
            'Vivienda': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Casa con patio, Apartamento, etc.'
            }),
            'Vacunas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Vacunas aplicadas y fechas...'
            }),
            'Compatibilidad_Mascota': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Cómo se lleva con otros animales, niños, etc.'
            }),
            'Descripción_Física': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción detallada de su apariencia'
            }),
            'Estado_Salud': forms.Select(attrs={'class': 'form-control'}),
            'Esterilizado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'Socializado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'foto_mascota': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'Origen': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'Nombre_Mascota': 'Nombre de la Mascota',
            'Fecha_Nacimiento': 'Fecha de Nacimiento',
            'Raza': 'Raza',
            'Genero': 'Género',
            'Peso': 'Peso (kg)',
            'Especie': 'Especie',
            'Color': 'Color/Patrón',
            'Tamaño': 'Tamaño',
            'Historial_Mascota': 'Historial de la Mascota',
            'Tipo_Alimentación': 'Tipo de Alimentación',
            'Enfermedades': 'Enfermedades o Condiciones',
            'Vivienda': 'Tipo de Vivienda Recomendado',
            'Vacunas': 'Registro de Vacunas',
            'Compatibilidad_Mascota': 'Compatibilidad con Otros Animales/Niños',
            'Descripción_Física': 'Descripción Física',
            'Estado_Salud': 'Estado de Salud Actual',
            'Esterilizado': '¿Está esterilizado/castrado?',
            'Socializado': '�Está socializado?',
            'foto_mascota': 'Foto de la Mascota',
            'Origen': 'Origen de la Mascota',
        }


class AdopcionForm(forms.ModelForm):
    """Formulario para que un propietario solicite una adopción"""
    
    class Meta:
        model = Adopcion
        fields = [
            'Motivo_Adopción', 'Lugar_Vivienda', 'Info_Mascota',
            'Estado_Ingreso_Mascota'
        ]
        widgets = {
            'Motivo_Adopción': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '¿Por qué deseas adoptar esta mascota?'
            }),
            'Lugar_Vivienda': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe tu vivienda (tipo, espacio, patio, etc.)'
            }),
            'Info_Mascota': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '¿Tienes otras mascotas? Describe el ambiente'
            }),
            'Estado_Ingreso_Mascota': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '¿Cómo planeas la adaptación de la mascota?'
            }),
        }
        labels = {
            'Motivo_Adopción': 'Motivo de la Adopción',
            'Lugar_Vivienda': 'Descripción de tu Vivienda',
            'Info_Mascota': 'Información sobre Mascotas Actuales',
            'Estado_Ingreso_Mascota': 'Plan de Adaptación de la Mascota',
        }
