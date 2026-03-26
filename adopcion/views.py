from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from rest_framework import viewsets, permissions, status, pagination
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Mascota, Adopcion
from .serializers import MascotaSerializer, AdopcionSerializer
from .forms import MascotaAdopcionForm, AdopcionForm
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime, date
from io import BytesIO


# ==================== VISTAS TRADICIONALES ====================

def mascotas(request):
    mascotas = Mascota.objects.all()
    context = {
        'mascotas': mascotas
    }
    return render(request, 'usuarios/mascotas.html', context)


def formulario_adopcion(request):
    """Redirige a la página de mascotas disponibles para adopción"""
    return redirect('mascotas_adopcion_disponibles')


@login_required
def registrar_mascota_adopcion(request):
    """Vista para que criadores registren mascotas en adopción"""
    # Verificar que el usuario sea Criador
    from usuarios.models import Criador
    
    usuario = request.user
    try:
        criador = Criador.objects.get(user=usuario)
    except:
        messages.error(request, "Solo los criadores pueden registrar mascotas en adopción")
        return redirect('index')
    
    if request.method == 'POST':
        form = MascotaAdopcionForm(request.POST, request.FILES)
        if form.is_valid():
            mascota = form.save(commit=False)
            mascota.idCriador = usuario.idUsuario
            mascota.disponible = True
            mascota.fecha_creacion = timezone.now()
            mascota.save()
            
            messages.success(request, f"✓ ¡{mascota.Nombre_Mascota} ha sido registrada exitosamente en adopción!")
            return redirect('mis_mascotas_adopcion')
        else:
            messages.error(request, "Error al registrar la mascota. Por favor verifica los datos.")
    else:
        form = MascotaAdopcionForm()
    
    context = {'form': form}
    return render(request, 'adopcion/registrar_mascota.html', context)


@login_required
def mis_mascotas_adopcion(request):
    """Vista para que criadores vean sus mascotas en adopción"""
    from usuarios.models import Criador
    
    usuario = request.user
    try:
        Criador.objects.get(user=usuario)
    except:
        messages.error(request, "Solo los criadores pueden acceder a esta función")
        return redirect('index')
    
    mascotas = Mascota.objects.filter(idCriador=usuario.idUsuario, disponible=True)
    context = {'mascotas': mascotas}
    return render(request, 'adopcion/mis_mascotas_adopcion.html', context)


def mascotas_adopcion_disponibles(request):
    """Vista para mostrar mascotas disponibles en adopción"""
    # Filtrar mascotas disponibles que NO han sido adoptadas
    mascotas = Mascota.objects.filter(
        disponible=True
    ).exclude(
        adopcion__Estado='Aprobada'
    ).distinct()
    
    # Filtros opcionales
    especie = request.GET.get('especie')
    tamaño = request.GET.get('tamaño')
    genero = request.GET.get('genero')
    
    if especie:
        mascotas = mascotas.filter(Especie__icontains=especie)
    if tamaño:
        mascotas = mascotas.filter(Tamaño__icontains=tamaño)
    if genero:
        mascotas = mascotas.filter(Genero=genero)
    
    # Ordenar por más recientes
    mascotas = mascotas.order_by('-fecha_creacion')
    
    context = {
        'mascotas': mascotas,
        'total_mascotas': mascotas.count()
    }
    return render(request, 'adopcion/mascotas_disponibles.html', context)


def detalles_mascota(request, mascota_id):
    """Vista para ver detalles de una mascota disponible"""
    try:
        mascota = Mascota.objects.get(idMascota=mascota_id, disponible=True)
    except Mascota.DoesNotExist:
        messages.error(request, "Mascota no encontrada")
        return redirect('mascotas_adopcion_disponibles')
    
    # Verificar si el usuario autenticado ya tiene una solicitud pendiente
    solicitud_existente = None
    if request.user.is_authenticated:
        solicitud_existente = Adopcion.objects.filter(
            idMascota=mascota,
            idPropietario=request.user.idUsuario,
            Estado__in=['Pendiente', 'Confirmada']
        ).first()
    
    context = {
        'mascota': mascota,
        'solicitud_existente': solicitud_existente
    }
    return render(request, 'adopcion/detalles_mascota.html', context)


@login_required
def solicitar_adopcion(request, mascota_id):
    """Vista para procesar una solicitud de adopción"""
    try:
        mascota = Mascota.objects.get(idMascota=mascota_id, disponible=True)
    except Mascota.DoesNotExist:
        messages.error(request, "Mascota no encontrada")
        return redirect('mascotas_adopcion_disponibles')
    
    # Verificar si ya existe una solicitud pendiente
    adopcion_existente = Adopcion.objects.filter(
        idMascota=mascota,
        idPropietario=request.user.idUsuario,
        Estado__in=['Pendiente', 'Confirmada']
    ).first()
    
    if adopcion_existente:
        messages.warning(request, "Ya tienes una solicitud pendiente para esta mascota")
        return redirect('detalles_mascota', mascota_id=mascota_id)
    
    if request.method == 'POST':
        form = AdopcionForm(request.POST)
        if form.is_valid():
            adopcion = form.save(commit=False)
            adopcion.idMascota = mascota
            adopcion.idPropietario = request.user.idUsuario
            adopcion.idCriador = mascota.idCriador
            adopcion.Estado = 'Pendiente'
            adopcion.Estado_Solicitud = 'En revisión'
            adopcion.Fecha_Solicitud = date.today()
            adopcion.Fecha_Adopción = date.today()
            adopcion.Fecha_Entrega = date.today()
            adopcion.Fuente_Mascota = mascota.Origen
            adopcion.save()
            
            messages.success(request, "✓ ¡Tu solicitud de adopción ha sido registrada! El criador la revisará pronto.")
            return redirect('mis_adopciones')
        else:
            messages.error(request, "Error al procesar la solicitud de adopción")
    else:
        form = AdopcionForm()
    
    context = {
        'form': form,
        'mascota': mascota
    }
    return render(request, 'adopcion/solicitar_adopcion.html', context)


@login_required
def mis_adopciones(request):
    """Vista para ver las adopciones del usuario actual"""
    adopciones = Adopcion.objects.filter(idPropietario=request.user.idUsuario).order_by('-Fecha_Solicitud')
    
    context = {
        'adopciones': adopciones,
        'total_adopciones': adopciones.count()
    }
    return render(request, 'adopcion/mis_adopciones.html', context)


@login_required
def descargar_reporte_adopcion(request, adopcion_id):
    """Vista para descargar reporte de adopción PDF"""
    try:
        # Obtener la adopción
        adopcion = Adopcion.objects.get(idAdopcion=adopcion_id)
        
        # Verificar que sea Aprobada
        if adopcion.Estado != 'Aprobada':
            return redirect('mis_adopciones')
        
        # Generar y descargar el PDF sin restricciones de permisos
        # (El usuario debe estar autenticado para llegar aquí por el @login_required)
        return generar_pdf_adopcion(adopcion)
            
    except Adopcion.DoesNotExist:
        return redirect('mis_adopciones')


@login_required
def solicitudes_adopcion_criador(request):
    """Vista para que criadores vean solicitudes de adopción de sus mascotas"""
    from usuarios.models import Criador
    
    usuario = request.user
    try:
        criador = Criador.objects.get(user=usuario)
    except:
        messages.error(request, "Solo los criadores pueden acceder a esta función")
        return redirect('index')
    
    # Obtener todas las solicitudes de adopción para mascotas del criador
    solicitudes = Adopcion.objects.filter(
        idCriador=usuario.idUsuario,
        Estado='Pendiente'
    ).order_by('-Fecha_Solicitud')
    
    # Obtener todas las mascotas del criador
    mascotas_criador = Mascota.objects.filter(idCriador=usuario.idUsuario)
    
    # Obtener solicitudes aprobadas también
    solicitudes_aprobadas = Adopcion.objects.filter(
        idCriador=usuario.idUsuario,
        Estado='Aprobada'
    ).order_by('-Fecha_Solicitud')
    
    context = {
        'solicitudes_pendientes': solicitudes,
        'solicitudes_aprobadas': solicitudes_aprobadas,
        'total_pendientes': solicitudes.count(),
        'total_aprobadas': solicitudes_aprobadas.count(),
    }
    return render(request, 'adopcion/solicitudes_adopcion.html', context)


@login_required
def aprobar_solicitud_adopcion(request, adopcion_id):
    """Vista para que criadores aprueben solicitudes de adopción"""
    from usuarios.models import Criador
    
    usuario = request.user
    try:
        criador = Criador.objects.get(user=usuario)
    except:
        messages.error(request, "Solo los criadores pueden aprobar solicitudes")
        return redirect('index')
    
    try:
        adopcion = Adopcion.objects.get(idAdopcion=adopcion_id, idCriador=usuario.idUsuario, Estado='Pendiente')
        adopcion.Estado = 'Aprobada'
        adopcion.Estado_Solicitud = 'Completada'
        adopcion.save()
        
        messages.success(request, f"✓ ¡Adopción de {adopcion.idMascota.Nombre_Mascota} aprobada! Se ha notificado al solicitante.")
        return redirect('solicitudes_adopcion_criador')
    except Adopcion.DoesNotExist:
        messages.error(request, "Solicitud de adopción no encontrada o no es tuya")
        return redirect('solicitudes_adopcion_criador')


@login_required
def rechazar_solicitud_adopcion(request, adopcion_id):
    """Vista para que criadores rechacen solicitudes de adopción"""
    from usuarios.models import Criador
    
    usuario = request.user
    try:
        criador = Criador.objects.get(user=usuario)
    except:
        messages.error(request, "Solo los criadores pueden rechazar solicitudes")
        return redirect('index')
    
    try:
        adopcion = Adopcion.objects.get(idAdopcion=adopcion_id, idCriador=usuario.idUsuario, Estado='Pendiente')
        adopcion.Estado = 'Rechazada'
        adopcion.Estado_Solicitud = 'Cancelada'
        adopcion.save()
        
        messages.success(request, f"✓ Solicitud de adopción rechazada. Se ha notificado al solicitante.")
        return redirect('solicitudes_adopcion_criador')
    except Adopcion.DoesNotExist:
        messages.error(request, "Solicitud de adopción no encontrada o no es tuya")
        return redirect('solicitudes_adopcion_criador')


# ==================== API VIEWSETS ====================

class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 1000


class MascotaViewSet(viewsets.ModelViewSet):
    queryset = Mascota.objects.all()
    serializer_class = MascotaSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_fields = ['Especie', 'Genero', 'Tamaño', 'Estado_Salud']
    search_fields = ['Nombre_Mascota', 'Raza', 'Especie']
    ordering_fields = ['Fecha_Nacimiento', 'Nombre_Mascota']
    ordering = ['-Fecha_Nacimiento']
    
    @action(detail=True, methods=['get'])
    def disponibles(self, request):
        """Obtener solo mascotas disponibles para adopción"""
        mascotas = Mascota.objects.exclude(adopcion__Estado='Aprobada').distinct()
        serializer = self.get_serializer(mascotas, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def solicitar_adopcion(self, request, pk=None):
        """Crear solicitud de adopción para una mascota"""
        mascota = self.get_object()
        from datetime import date
        
        try:
            adopcion = Adopcion.objects.create(
                idMascota=mascota,
                idPropietario=request.user.idUsuario,
                Estado='Pendiente',
                Fecha_Solicitud=date.today(),
                Fecha_Adopción=date.today(),
                Fecha_Entrega=date.today(),
                Estado_Solicitud='En revisión',
                Motivo_Adopción=request.data.get('motivo', ''),
                Fuente_Mascota='Criador',
                Control_Adopción='',
                Estado_Salud_Mascota='',
                Lugar_Vivienda='',
                Info_Mascota='',
                Estado_Ingreso_Mascota='',
                Devolución='',
            )
            return Response(
                {'mensaje': 'Solicitud de adopción creada', 'id': adopcion.idAdopcion},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class AdopcionViewSet(viewsets.ModelViewSet):
    serializer_class = AdopcionSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_fields = ['Estado', 'Estado_Solicitud', 'Fuente_Mascota']
    ordering_fields = ['Fecha_Solicitud']
    ordering = ['-Fecha_Solicitud']
    
    def get_queryset(self):
        """Filtrar adopciones del usuario actual"""
        user = self.request.user
        return Adopcion.objects.filter(idPropietario=user.idUsuario)
    
    @action(detail=False, methods=['get'])
    def mis_adopciones(self, request):
        """Obtener las adopciones del usuario actual"""
        adopciones = self.get_queryset()
        serializer = self.get_serializer(adopciones, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def aprobar(self, request, pk=None):
        """Aprobar una solicitud de adopción"""
        adopcion = self.get_object()
        adopcion.Estado = 'Aprobada'
        adopcion.Estado_Solicitud = 'Completada'
        adopcion.save()
        serializer = self.get_serializer(adopcion)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def rechazar(self, request, pk=None):
        """Rechazar una solicitud de adopción"""
        adopcion = self.get_object()
        adopcion.Estado = 'Rechazada'
        adopcion.Estado_Solicitud = 'Cancelada'
        adopcion.save()
        serializer = self.get_serializer(adopcion)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def descargar_pdf(self, request, pk=None):
        """Descargar reporte de adopción en PDF"""
        adopcion = self.get_object()
        return generar_pdf_adopcion(adopcion)


# ==================== FUNCIONES PARA GENERAR PDF ====================

def generar_pdf_adopcion(adopcion):
    """Genera un PDF con el reporte de adopción"""
    buffer = BytesIO()
    
    # Crear documento PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
    )
    
    # Lista para almacenar elementos del PDF
    elementos = []
    
    # Estilos
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle(
        'titulo_custom',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#e83e8c'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitulo_style = ParagraphStyle(
        'subtitulo_custom',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#a8419f'),
        spaceAfter=12,
        alignment=TA_CENTER,
    )
    
    heading_style = ParagraphStyle(
        'heading_custom',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=10,
        fontName='Helvetica-Bold',
    )
    
    normal_style = ParagraphStyle(
        'normal_custom',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
    )
    
    # Título
    elementos.append(Paragraph('🐾 REPORTE DE ADOPCIÓN', titulo_style))
    elementos.append(Spacer(1, 0.15*inch))
    
    # Fecha de generación
    fecha_generacion = datetime.now().strftime('%d de %B de %Y a las %H:%M:%S')
    elementos.append(Paragraph(f'Generado: {fecha_generacion}', styles['Normal']))
    elementos.append(Spacer(1, 0.25*inch))
    
    # Información de la adopción
    elementos.append(Paragraph('INFORMACIÓN DE LA ADOPCIÓN', heading_style))
    
    info_adopcion = [
        ['ID de Adopción:', str(adopcion.idAdopcion)],
        ['Estado:', adopcion.Estado],
        ['Estado de Solicitud:', adopcion.Estado_Solicitud],
        ['Fecha de Solicitud:', str(adopcion.Fecha_Solicitud)],
        ['Fecha de Adopción:', str(adopcion.Fecha_Adopción)],
        ['Fecha de Entrega:', str(adopcion.Fecha_Entrega)],
    ]
    
    tabla_adopcion = Table(info_adopcion, colWidths=[2.5*inch, 3.5*inch])
    tabla_adopcion.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5e6e1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    elementos.append(tabla_adopcion)
    elementos.append(Spacer(1, 0.25*inch))
    
    # Información de la mascota
    elementos.append(Paragraph('INFORMACIÓN DE LA MASCOTA', heading_style))
    
    try:
        mascota = adopcion.idMascota
        info_mascota = [
            ['Nombre:', mascota.Nombre_Mascota],
            ['Especie:', mascota.Especie],
            ['Raza:', mascota.Raza],
            ['Género:', mascota.Genero],
            ['Tamaño:', mascota.Tamaño],
            ['Estado de Salud:', mascota.Estado_Salud],
            ['Fecha de Nacimiento:', str(mascota.Fecha_Nacimiento)],
        ]
        
        tabla_mascota = Table(info_mascota, colWidths=[2.5*inch, 3.5*inch])
        tabla_mascota.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5e6e1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        elementos.append(tabla_mascota)
    except:
        elementos.append(Paragraph('Información de mascota no disponible', styles['Normal']))
    
    elementos.append(Spacer(1, 0.25*inch))
    
    # Información adicional
    if adopcion.Motivo_Adopción:
        elementos.append(Paragraph('MOTIVO DE ADOPCIÓN', heading_style))
        elementos.append(Paragraph(adopcion.Motivo_Adopción, normal_style))
        elementos.append(Spacer(1, 0.15*inch))
    
    # Pie de página
    elementos.append(Spacer(1, 0.35*inch))
    elementos.append(Paragraph('Este documento es un reporte oficial de Hairy Love', styles['Normal']))
    elementos.append(Paragraph('Para más información, visite www.hairylove.com', styles['Normal']))
    
    # Construir PDF
    doc.build(elementos)
    
    # Preparar respuesta
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="adopcion_{adopcion.idAdopcion}_reporte.pdf"'
    
    return response

