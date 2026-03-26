from django import forms
from .models import Usuario, Propietario, Criador, Especialista


class EditarPerfilForm(forms.ModelForm):
    """Formulario para editar datos personales del usuario"""
    
    class Meta:
        model = Usuario
        fields = ['nombre', 'apellido', 'telefono', 'correo', 'direccion', 'fecha_nacimiento', 'foto_perfil']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Nombre',
                'required': 'required'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Apellido',
                'required': 'required'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '+57 3XX XXXX XXX',
                'type': 'tel'
            }),
            'correo': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'correo@ejemplo.com',
                'required': 'required'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Tu dirección completa'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'foto_perfil': forms.FileInput(attrs={
                'class': 'form-input',
                'accept': 'image/*'
            }),
        }


class EditarCriadorForm(forms.ModelForm):
    """Formulario para editar datos específicos del Criador"""
    
    class Meta:
        model = Criador
        fields = ['Tipo_Criador', 'Razon_Dar_Adopcion', 'Condiciones_Adopcion', 'Informacion_Rescate']
        widgets = {
            'Tipo_Criador': forms.Select(attrs={
                'class': 'form-input'
            }),
            'Razon_Dar_Adopcion': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': '¿Por qué das en adopción?',
                'rows': 4
            }),
            'Condiciones_Adopcion': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Condiciones especiales para la adopción',
                'rows': 4
            }),
            'Informacion_Rescate': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Información sobre rescate de animales',
                'rows': 4
            }),
        }


class EditarPropietarioForm(forms.ModelForm):
    """Formulario para editar datos específicos del Propietario"""
    
    class Meta:
        model = Propietario
        fields = ['Preferencia_Mascota']
        widgets = {
            'Preferencia_Mascota': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ej: Perros pequeños, Gatos, etc.'
            }),
        }


class EditarEspecialistaForm(forms.ModelForm):
    """Formulario para editar datos específicos del Especialista"""
    
    class Meta:
        model = Especialista
        fields = ['Especialidad', 'Años_Experiencia', 'Horario', 'Certificados']
        widgets = {
            'Especialidad': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ej: Veterinario, Peluquero, Entrenador'
            }),
            'Años_Experiencia': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0',
                'min': '0'
            }),
            'Horario': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ej: Lunes a Viernes 9AM-6PM'
            }),
            'Certificados': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Certificaciones y diplomas',
                'rows': 4
            }),
        }
