from django.db import models
from django.utils import timezone

class Mascota(models.Model):
    GENERO_CHOICES = [
        ('Macho', 'Macho'),
        ('Hembra', 'Hembra'),
    ]

    ORIGEN_CHOICES = [
        ('Criador', 'Criador'),
        ('Refugio', 'Refugio'),
        ('Rescate', 'Rescate'),
        ('Abandono', 'Abandono'),
    ]

    ESTADO_SALUD_CHOICES = [
        ('Excelente', 'Excelente'),
        ('Buena', 'Buena'),
        ('Regular', 'Regular'),
        ('Mala', 'Mala'),
        ('Crítica', 'Crítica'),
    ]

    idMascota = models.AutoField(primary_key=True)
    Nombre_Mascota = models.CharField(max_length=100)
    Fecha_Nacimiento = models.DateField()
    Raza = models.CharField(max_length=100)
    Genero = models.CharField(max_length=6, choices=GENERO_CHOICES)
    Peso = models.FloatField()
    Especie = models.CharField(max_length=50)
    Color = models.CharField(max_length=50)
    Tamaño = models.CharField(max_length=50)
    Historial_Mascota = models.TextField()
    Origen = models.CharField(max_length=10, choices=ORIGEN_CHOICES, default='Criador')
    Tipo_Alimentación = models.CharField(max_length=100)
    Enfermedades = models.TextField()
    Vivienda = models.CharField(max_length=100)
    Vacunas = models.TextField()
    Compatibilidad_Mascota = models.TextField()
    Descripción_Física = models.TextField()
    idCriador = models.IntegerField(null=True, blank=True)
    Estado_Salud = models.CharField(max_length=10, choices=ESTADO_SALUD_CHOICES, default='Buena')
    Esterilizado = models.BooleanField(default=False)
    Socializado = models.BooleanField(default=True)
    
    # NUEVOS CAMPOS
    foto_mascota = models.ImageField(upload_to='mascotas/', null=True, blank=True)
    disponible = models.BooleanField(default=True)
    puntuacion = models.DecimalField(max_digits=3, decimal_places=2, default=0)  # Rating 0-5
    numero_personas_interesadas = models.PositiveIntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.Nombre_Mascota



class Adopcion(models.Model):
    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Aprobada', 'Aprobada'),
        ('Rechazada', 'Rechazada'),
    ]

    ESTADO_SOLICITUD_CHOICES = [
        ('En revisión', 'En revisión'),
        ('Completada', 'Completada'),
        ('Cancelada', 'Cancelada'),
    ]

    FUENTE_MASCOTA_CHOICES = [
        ('Criador', 'Criador'),
        ('Refugio', 'Refugio'),
        ('Rescate', 'Rescate'),
    ]

    idAdopcion = models.AutoField(primary_key=True)
    idPropietario = models.IntegerField()  
    idMascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)
    idCriador = models.IntegerField(null=True, blank=True)  
    Estado = models.CharField(max_length=50, choices=ESTADO_CHOICES)
    Fecha_Solicitud = models.DateField()
    Fecha_Adopción = models.DateField()
    Fecha_Entrega = models.DateField()
    Motivo_Adopción = models.TextField()
    Control_Adopción = models.TextField()
    Estado_Salud_Mascota = models.TextField()
    Lugar_Vivienda = models.TextField()
    Info_Mascota = models.TextField()
    Estado_Ingreso_Mascota = models.TextField()
    Devolución = models.TextField()
    Estado_Solicitud = models.CharField(max_length=50, choices=ESTADO_SOLICITUD_CHOICES)
    Fuente_Mascota = models.CharField(max_length=10, choices=FUENTE_MASCOTA_CHOICES, default='Criador')

    def __str__(self):
        return f"Adopción {self.idAdopcion} - Mascota {self.idMascota.Nombre_Mascota}"