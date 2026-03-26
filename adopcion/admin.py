from django.contrib import admin
from .models import Mascota, Adopcion

@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    list_display = ('idMascota', 'Nombre_Mascota', 'Especie', 'Raza', 'Genero', 'Estado_Salud')
    list_filter = ('Especie', 'Raza', 'Genero', 'Estado_Salud', 'Esterilizado', 'Socializado')
    search_fields = ('Nombre_Mascota', 'Raza', 'Especie')
    readonly_fields = ('idMascota',)

@admin.register(Adopcion)
class AdopcionAdmin(admin.ModelAdmin):
    list_display = ('idAdopcion', 'idMascota', 'Estado', 'Fecha_Solicitud')
    list_filter = ('Estado', 'Fecha_Solicitud')
    search_fields = ('idMascota__Nombre_Mascota',)
    readonly_fields = ('idAdopcion',)
