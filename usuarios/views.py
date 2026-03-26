from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from rest_framework import viewsets, permissions, status, pagination
from rest_framework.decorators import action
from rest_framework.response import Response
from adopcion.models import Mascota, Adopcion
from servicios.models import Servicio, SolicitudServicio
from .models import Usuario, Propietario, Criador, Especialista, PasswordResetToken
from .serializers import UsuarioSerializer, PropietarioSerializer, CriadorSerializer, EspecialistaSerializer
from datetime import date
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import uuid


# ==================== VISTAS TRADICIONALES ====================

def principal(request):
    mascotas = Mascota.objects.all()[:6]
    context = {'mascotas': mascotas}
    return render(request, 'usuarios/principal.html', context)


def inicio_sesion(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        password = request.POST.get('password')

        try:
            usuario = Usuario.objects.get(correo=correo)

            if check_password(password, usuario.password):
                # Autenticar al usuario correctamente en el sistema de Django
                login(request, usuario)
                request.session['usuario_id'] = usuario.idUsuario
                request.session['usuario_nombre'] = f"{usuario.nombre} {usuario.apellido}"
                request.session['usuario_tipo'] = usuario.tipo
                request.session['usuario_correo'] = usuario.correo
                
                messages.success(request, f"¡Bienvenido {usuario.nombre}!")
                
                if usuario.tipo == 'Propietario':
                    return redirect('propietario') 
                elif usuario.tipo == 'Criador':
                    return redirect('criador')     
                elif usuario.tipo == 'Especialista':
                    return redirect('especialista') 
                else:
                    return redirect('index')    
            else:
                messages.error(request, "Contraseña incorrecta")
                
        except Usuario.DoesNotExist:
            messages.error(request, "Usuario no registrado con ese correo")
            
    return render(request, 'usuarios/inicio_sesion.html')


def cerrar_sesion(request):
    request.session.flush() 
    messages.success(request, "Has cerrado sesión correctamente")
    return redirect('index')


# ==================== VISTAS DE RECUPERACIÓN DE CONTRASEÑA ====================

import random

def solicitar_reset_contrasena(request):
    """Vista para solicitar reset de contraseña - Envía código de 6 dígitos"""
    if request.method == 'POST':
        correo = request.POST.get('correo')
        
        try:
            usuario = Usuario.objects.get(correo=correo)
            
            # Generar código aleatorio de 6 dígitos
            codigo = str(random.randint(100000, 999999))
            
            # Crear token con código
            token = PasswordResetToken.objects.create(
                user=usuario,
                token=str(uuid.uuid4()),
                codigo=codigo,
                expires_at=timezone.now() + timedelta(minutes=15)  # 15 minutos
            )
            
            # Enviar email con código
            asunto = "🔐 Código de verificación - Hairy Love"
            mensaje = f"""
Hola {usuario.nombre},

Se realizó una solicitud para recuperar tu contraseña en Hairy Love.

Tu código de verificación es:

    {codigo}

Este código expirará en 15 minutos.

Si no realizaste esta solicitud, ignora este mensaje.

---
Equipo Hairy Love
"""
            
            try:
                send_mail(
                    asunto,
                    mensaje,
                    settings.DEFAULT_FROM_EMAIL,
                    [correo],
                    fail_silently=False,
                )
                # Guardar código en sesión para verificación
                request.session['codigo_usuario'] = correo
                messages.success(request, f"Se ha enviado un código de verificación a {correo}")
                return redirect('verificar_codigo_reset')
            except Exception as e:
                messages.error(request, f"Error enviando email: {str(e)}")
                
        except Usuario.DoesNotExist:
            # No revelar si el email existe por seguridad
            messages.success(request, "Si el correo existe en nuestro sistema, recibirás un código de verificación.")
    
    return render(request, 'usuarios/solicitar_reset.html')


def verificar_codigo_reset(request):
    """Vista para verificar el código y resetear contraseña"""
    correo_usuario = request.session.get('codigo_usuario')
    
    if not correo_usuario:
        messages.error(request, "Debes solicitar un código primero")
        return redirect('solicitar_reset_contrasena')
    
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        nueva_contrasena = request.POST.get('nueva_contrasena')
        confirmar_contrasena = request.POST.get('confirmar_contrasena')
        
        try:
            usuario = Usuario.objects.get(correo=correo_usuario)
            
            # Buscar el código válido más reciente
            token_obj = PasswordResetToken.objects.filter(
                user=usuario,
                codigo=codigo,
                used=False
            ).order_by('-created_at').first()
            
            if not token_obj:
                messages.error(request, "Código inválido o expirado")
                return render(request, 'usuarios/verificar_codigo.html')
            
            if not token_obj.is_valid():
                messages.error(request, "El código ha expirado. Solicita uno nuevo.")
                return redirect('solicitar_reset_contrasena')
            
            # Validar contraseña
            if nueva_contrasena != confirmar_contrasena:
                messages.error(request, "Las contraseñas no coinciden")
                return render(request, 'usuarios/verificar_codigo.html', {'codigo': codigo})
            
            if len(nueva_contrasena) < 8:
                messages.error(request, "La contraseña debe tener al menos 8 caracteres")
                return render(request, 'usuarios/verificar_codigo.html', {'codigo': codigo})
            
            # Validar requisitos de contraseña
            import re
            if not re.search(r'[A-Z]', nueva_contrasena):
                messages.error(request, "La contraseña debe contener al menos una mayúscula")
                return render(request, 'usuarios/verificar_codigo.html', {'codigo': codigo})
            
            if not re.search(r'[a-z]', nueva_contrasena):
                messages.error(request, "La contraseña debe contener al menos una minúscula")
                return render(request, 'usuarios/verificar_codigo.html', {'codigo': codigo})
            
            if not re.search(r'[0-9]', nueva_contrasena):
                messages.error(request, "La contraseña debe contener al menos un número")
                return render(request, 'usuarios/verificar_codigo.html', {'codigo': codigo})
            
            if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'"|,.<>/?]', nueva_contrasena):
                messages.error(request, "La contraseña debe contener al menos un carácter especial")
                return render(request, 'usuarios/verificar_codigo.html', {'codigo': codigo})
            
            # Actualizar contraseña
            usuario.set_password(nueva_contrasena)
            usuario.save()
            
            # Marcar token como usado
            token_obj.mark_as_used()
            
            # Limpiar sesión
            del request.session['codigo_usuario']
            
            messages.success(request, "Tu contraseña ha sido actualizada correctamente. Inicia sesión con tu nueva contraseña.")
            return redirect('login')
        
        except Usuario.DoesNotExist:
            messages.error(request, "Usuario no encontrado")
            return redirect('solicitar_reset_contrasena')
    
    return render(request, 'usuarios/verificar_codigo.html')


def reset_contrasena(request, token):
    """Vista antigua para retrocompatibilidad - Redirige al nuevo sistema"""
    messages.info(request, "Usa el nuevo sistema de códigos de verificación")
    return redirect('solicitar_reset_contrasena')


def registro(request):
    if request.method == "POST":
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        correo = request.POST.get('correo')
        password = request.POST.get('password')
        tipo = request.POST.get('tipo')
        telefono = request.POST.get('telefono', '')
        direccion = request.POST.get('direccion', '')

        try:
            usuario = Usuario.objects.create_user(
                username=correo,
                correo=correo,
                password=password,
                nombre=nombre,
                apellido=apellido,
                tipo=tipo,
                telefono=telefono,
                direccion=direccion,
            )
            
            # Crear perfil específico según tipo
            if tipo == 'Propietario':
                Propietario.objects.create(user=usuario)
            elif tipo == 'Criador':
                Criador.objects.create(user=usuario)
            elif tipo == 'Especialista':
                Especialista.objects.create(user=usuario)

            messages.success(request, "Usuario registrado correctamente")
            return redirect('login')
        except Exception as e:
            messages.error(request, f"Error en el registro: {str(e)}")

    return render(request, 'usuarios/registro.html')


@login_required
def perfil_propietario(request):
    try:
        propietario = Propietario.objects.get(user=request.user)
    except Propietario.DoesNotExist:
        propietario = None
    
    # Obtener las adopciones del propietario
    adopciones = Adopcion.objects.filter(idPropietario=request.user.idUsuario).order_by('-Fecha_Solicitud') if hasattr(request.user, 'idUsuario') else []
    
    # Obtener las mascotas adoptadas (aprobadas)
    mascotas_adoptadas = [adopcion.idMascota for adopcion in adopciones if adopcion.Estado == 'Aprobada']
    
    context = {
        'mascotas_adoptadas': mascotas_adoptadas,
        'adopciones': adopciones,
        'propietario': propietario,
        'total_adopciones': adopciones.count(),
        'total_adoptadas': len(mascotas_adoptadas),
    }
    return render(request, 'usuarios/perfilPropietario.html', context)


@login_required
def perfil_criador(request):
    try:
        criador = Criador.objects.get(user=request.user)
    except Criador.DoesNotExist:
        criador = None
    
    mascotas = Mascota.objects.filter(idCriador=criador.idCriador) if criador else []
    context = {
        'criador': criador,
        'mascotas': mascotas,
    }
    return render(request, 'usuarios/perfilCriador.html', context)


@login_required
def perfil_especialista(request):
    try:
        especialista = Especialista.objects.get(user=request.user)
    except Especialista.DoesNotExist:
        especialista = None
    
    context = {
        'especialista': especialista,
    }
    return render(request, 'usuarios/perfilEspecialista.html', context)


@login_required
def editar_perfil(request):
    """Vista para editar perfil del usuario"""
    from .forms import EditarPerfilForm, EditarCriadorForm, EditarPropietarioForm, EditarEspecialistaForm
    
    usuario = request.user
    perfil_tipo = usuario.tipo
    
    if request.method == 'POST':
        form_usuario = EditarPerfilForm(request.POST, request.FILES, instance=usuario)
        
        # Formularios específicos según el tipo de usuario
        form_especifico = None
        if perfil_tipo == 'Criador':
            try:
                criador = Criador.objects.get(user=usuario)
                form_especifico = EditarCriadorForm(request.POST, instance=criador)
            except Criador.DoesNotExist:
                form_especifico = None
        elif perfil_tipo == 'Propietario':
            try:
                propietario = Propietario.objects.get(user=usuario)
                form_especifico = EditarPropietarioForm(request.POST, instance=propietario)
            except Propietario.DoesNotExist:
                form_especifico = None
        elif perfil_tipo == 'Especialista':
            try:
                especialista = Especialista.objects.get(user=usuario)
                form_especifico = EditarEspecialistaForm(request.POST, instance=especialista)
            except Especialista.DoesNotExist:
                form_especifico = None
        
        # Validar y guardar
        if form_usuario.is_valid():
            form_usuario.save()
            
            if form_especifico and form_especifico.is_valid():
                form_especifico.save()
            
            messages.success(request, "✓ Perfil actualizado exitosamente")
            
            # Redirigir al perfil correspondiente
            if perfil_tipo == 'Criador':
                return redirect('criador')
            elif perfil_tipo == 'Propietario':
                return redirect('propietario')
            elif perfil_tipo == 'Especialista':
                return redirect('especialista')
            else:
                return redirect('index')
        else:
            messages.error(request, "Error al actualizar el perfil. Verifica los datos.")
    else:
        form_usuario = EditarPerfilForm(instance=usuario)
        form_especifico = None
        
        if perfil_tipo == 'Criador':
            try:
                criador = Criador.objects.get(user=usuario)
                form_especifico = EditarCriadorForm(instance=criador)
            except Criador.DoesNotExist:
                pass
        elif perfil_tipo == 'Propietario':
            try:
                propietario = Propietario.objects.get(user=usuario)
                form_especifico = EditarPropietarioForm(instance=propietario)
            except Propietario.DoesNotExist:
                pass
        elif perfil_tipo == 'Especialista':
            try:
                especialista = Especialista.objects.get(user=usuario)
                form_especifico = EditarEspecialistaForm(instance=especialista)
            except Especialista.DoesNotExist:
                pass
    
    context = {
        'form_usuario': form_usuario,
        'form_especifico': form_especifico,
        'perfil_tipo': perfil_tipo,
    }
    return render(request, 'usuarios/editar_perfil.html', context)


@login_required
@require_http_methods(["POST"])
def actualizar_foto(request):
    try:
        usuario = request.user
        if 'foto_perfil' in request.FILES:
            usuario.foto_perfil = request.FILES['foto_perfil']
            usuario.save()
            messages.success(request, "Foto de perfil actualizada")
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
    
    return redirect(request.META.get('HTTP_REFERER', 'index'))


def formularioServicios(request):
    """Vista para mostrar el formulario de solicitud de servicios"""
    if request.method == 'POST':
        # Procesar solicitud POST
        if not request.user.is_authenticated:
            messages.error(request, "Debes iniciar sesión para solicitar un servicio")
            return redirect('inicio_sesion')
        
        try:
            mascota_id = request.POST.get('mascota')
            servicio_id = request.POST.get('servicio')
            fecha = request.POST.get('fecha_programada')
            hora = request.POST.get('hora_programada')
            descripcion = request.POST.get('descripcion_problema', '')
            
            # Validar que la mascota pertenece al usuario
            mascota = Mascota.objects.get(idMascota=mascota_id, propietario=request.user)
            servicio = Servicio.objects.get(idServicio=servicio_id)
            
            # Combinar fecha y hora
            from datetime import datetime
            fecha_hora = datetime.combine(
                datetime.strptime(fecha, '%Y-%m-%d').date(),
                datetime.strptime(hora, '%H:%M').time()
            )
            
            # Crear solicitud de servicio
            solicitud = SolicitudServicio.objects.create(
                servicio=servicio,
                mascota=mascota,
                usuario=request.user,
                fecha_programada=fecha_hora,
                descripcion_problema=descripcion
            )
            
            messages.success(request, f"✓ ¡Solicitud registrada exitosamente! Un especialista se pondrá en contacto contigo pronto.")
            return redirect('propietario')
            
        except Mascota.DoesNotExist:
            messages.error(request, "Mascota no encontrada o no tienes permiso para acceder a ella")
        except Servicio.DoesNotExist:
            messages.error(request, "Servicio no encontrado")
        except Exception as e:
            messages.error(request, f"Error al procesar la solicitud: {str(e)}")
    
    # Mostrar formulario GET
    servicios = Servicio.objects.filter(disponible=True)
    context = {'servicios': servicios}
    return render(request, 'servicios/formularioServicios.html', context)


def mascotas_adopcion(request):
    """Vista para mostrar todas las mascotas disponibles para adopción"""
    mascotas = Mascota.objects.all()
    
    # Filtros
    especie = request.GET.get('especie')
    raza = request.GET.get('raza')
    genero = request.GET.get('genero')
    estado_salud = request.GET.get('estado_salud')
    esterilizado = request.GET.get('esterilizado')
    busqueda = request.GET.get('busqueda')
    
    if especie:
        mascotas = mascotas.filter(Especie=especie)
    if raza:
        mascotas = mascotas.filter(Raza=raza)
    if genero:
        mascotas = mascotas.filter(Genero=genero)
    if estado_salud:
        mascotas = mascotas.filter(Estado_Salud=estado_salud)
    if esterilizado:
        mascotas = mascotas.filter(Esterilizado=esterilizado.lower() == 'true')
    if busqueda:
        from django.db.models import Q
        mascotas = mascotas.filter(
            Q(Nombre_Mascota__icontains=busqueda) |
            Q(Raza__icontains=busqueda) |
            Q(Color__icontains=busqueda)
        )
    
    context = {
        'mascotas': mascotas,
    }
    return render(request, 'usuarios/mascotas_mejorado.html', context)


# ==================== VISTAS DE FAVORITOS ====================

@login_required
@require_http_methods(["POST"])
def toggle_favorito(request):
    """Agregar o remover un favorito (AJAX)"""
    from .models import Favorito
    import json
    
    try:
        data = json.loads(request.body)
        tipo_contenido = data.get('tipo')  # 'mascota' o 'servicio'
        id_contenido = data.get('id')
        nombre = data.get('nombre', 'Favorito')
        
        if not tipo_contenido or not id_contenido:
            return Response({'error': 'Faltan parámetros'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar si ya existe
        favorito = Favorito.objects.filter(
            usuario=request.user,
            tipo_contenido=tipo_contenido,
            id_contenido=id_contenido
        ).first()
        
        if favorito:
            # Remover favorito
            favorito.delete()
            return Response({
                'success': True,
                'mensaje': 'Favorito eliminado',
                'es_favorito': False
            }, status=status.HTTP_200_OK)
        else:
            # Agregar favorito
            Favorito.objects.create(
                usuario=request.user,
                tipo_contenido=tipo_contenido,
                id_contenido=id_contenido,
                nombre_contenido=nombre
            )
            return Response({
                'success': True,
                'mensaje': 'Agregado a favoritos',
                'es_favorito': True
            }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@login_required
def mis_favoritos(request):
    """Ver todos los favoritos del usuario"""
    from .models import Favorito
    
    favoritos = Favorito.objects.filter(usuario=request.user)
    mascotas_favoritas = []
    servicios_favoritos = []
    
    for fav in favoritos:
        if fav.tipo_contenido == 'mascota':
            try:
                mascota = Mascota.objects.get(idMascota=fav.id_contenido)
                mascotas_favoritas.append(mascota)
            except Mascota.DoesNotExist:
                fav.delete()  # Eliminar favorito huérfano
        elif fav.tipo_contenido == 'servicio':
            try:
                from servicios.models import Servicio
                servicio = Servicio.objects.get(idServicio=fav.id_contenido)
                servicios_favoritos.append(servicio)
            except:
                fav.delete()  # Eliminar favorito huérfano
    
    context = {
        'mascotas_favoritas': mascotas_favoritas,
        'servicios_favoritos': servicios_favoritos,
        'total_favoritos': len(mascotas_favoritas) + len(servicios_favoritos)
    }
    return render(request, 'usuarios/mis_favoritos.html', context)


# ==================== API VIEWSETS ====================

class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


class UsuarioViewSet(viewsets.ModelViewSet):
    serializer_class = UsuarioSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_fields = ['tipo']
    search_fields = ['nombre', 'apellido', 'correo']
    
    def get_queryset(self):
        return Usuario.objects.all()
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Obtener información del usuario actual"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class PropietarioViewSet(viewsets.ModelViewSet):
    queryset = Propietario.objects.all()
    serializer_class = PropietarioSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def mascotas(self, request, pk=None):
        """Obtener mascotas de un propietario"""
        propietario = self.get_object()
        mascotas = Mascota.objects.filter(idCriador=propietario.idPropietario)
        serializer = self.get_serializer(mascotas, many=True)
        return Response(serializer.data)


class CriadorViewSet(viewsets.ModelViewSet):
    queryset = Criador.objects.all()
    serializer_class = CriadorSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_fields = ['Estado_Verificacion', 'Tipo_Criador']


class EspecialistaViewSet(viewsets.ModelViewSet):
    queryset = Especialista.objects.all()
    serializer_class = EspecialistaSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_fields = ['Especialidad']
    search_fields = ['Especialidad', 'user__nombre']


