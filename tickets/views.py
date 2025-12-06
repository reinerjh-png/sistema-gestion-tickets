import os
from django.conf import settings
from django.db.models import Count, Sum, Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from .forms import (
    GenerarTicketsForm,
    RepartirTicketsForm,
    LoginTicketForm,
    RegistrarCompradorForm
)
from .models import Ticket, Comprador

def bienvenida(request):
    return render(request, 'tickets/bienvenida.html')

def generar_tickets(request):
    if request.method == 'POST':
        form = GenerarTicketsForm(request.POST)
        if form.is_valid():
            inicio = form.cleaned_data['numero_inicial']
            fin = form.cleaned_data['numero_final']
            precio = form.cleaned_data['precio']

            for numero in range(inicio, fin + 1):
                Ticket.objects.create(
                    numero=numero,
                    precio=precio
                )

            return redirect('generar_tickets')
    else:
        form = GenerarTicketsForm()

    return render(request, 'tickets/generar_tickets.html', {'form': form})

def repartir_tickets(request):
    disponibles = Ticket.objects.filter(estado='DISPONIBLE').order_by('numero')

    rango_disponible = None
    if disponibles.exists():
        rango_disponible = f"{disponibles.first().numero} hasta {disponibles.last().numero}"

    if request.method == 'POST':
        form = RepartirTicketsForm(request.POST)
        if form.is_valid():
            inicio = form.cleaned_data['numero_inicio']
            fin = form.cleaned_data['numero_fin']
            vendedor = form.cleaned_data['vendedor']

            tickets = Ticket.objects.filter(
                numero__gte=inicio,
                numero__lte=fin,
                estado='DISPONIBLE'
            )

            for ticket in tickets:
                ticket.vendedor = vendedor
                ticket.estado = 'ASIGNADO'
                ticket.save()

            return redirect('repartir_tickets')
    else:
        form = RepartirTicketsForm()

    return render(request, 'tickets/repartir_tickets.html', {
        'form': form,
        'rango_disponible': rango_disponible
    })

def login_ticket(request):
    if request.method == 'POST':
        form = LoginTicketForm(request.POST)
        if form.is_valid():
            numero = form.cleaned_data['numero']
            codigo = form.cleaned_data['codigo']

            try:
                ticket = Ticket.objects.get(numero=numero, codigo=codigo)

                if ticket.estado == 'VENDIDO':
                    return render(request, 'tickets/login_ticket.html', {
                        'form': form,
                        'error': 'Este ticket ya fue registrado.'
                    })

                return redirect('registrar_comprador', ticket_id=ticket.id)

            except Ticket.DoesNotExist:
                return render(request, 'tickets/login_ticket.html', {
                    'form': form,
                    'error': 'Ticket o código incorrectos.'
                })
    else:
        form = LoginTicketForm()

    return render(request, 'tickets/login_ticket.html', {'form': form})

def registrar_comprador(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == 'POST':
        form = RegistrarCompradorForm(request.POST)
        if form.is_valid():
            comprador = form.save(commit=False)
            comprador.ticket = ticket
            comprador.save()

            ticket.estado = 'VENDIDO'
            ticket.save()

            return render(request, 'tickets/registro_exitoso.html')
    else:
        form = RegistrarCompradorForm()

    return render(request, 'tickets/registrar_comprador.html', {
        'form': form,
        'ticket': ticket
    })

def reporte_general(request):
    total_tickets = Ticket.objects.filter(estado='VENDIDO').count()

    total_dinero = Ticket.objects.filter(
        estado='VENDIDO'
    ).aggregate(total=Sum('precio'))['total'] or 0

    por_vendedor = Ticket.objects.filter(
        vendedor__isnull=False   # ✅ elimina el None
    ).values(
        'vendedor__nombres'
    ).annotate(
        vendidos=Count('id', filter=Q(estado='VENDIDO')),
        no_vendidos=Count('id', filter=~Q(estado='VENDIDO')),  # ✅ todo lo que NO esté vendido
        dinero=Sum('precio', filter=Q(estado='VENDIDO'))
    )

    return render(request, 'tickets/reporte_general.html', {
        'total_tickets': total_tickets,
        'total_dinero': total_dinero,
        'por_vendedor': por_vendedor
    })

def reporte_detallado(request):
    vendidos = Comprador.objects.select_related('ticket', 'ticket__vendedor')

    return render(request, 'tickets/reporte_detallado.html', {
        'vendidos': vendidos
    })

def exportar_reporte_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="mini_tickets_sorteo.pdf"'

    c = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # COLORES
    honda_red = colors.HexColor("#DC002E")
    dark_grey = colors.HexColor("#222222")
    border_color = colors.HexColor("#DDDDDD")
    
    # DIMENSIONES (Más compactas)
    ticket_width = 5.5 * cm
    ticket_height = 3.8 * cm  # Reducido de 4.5cm a 3.8cm
    
    margin_x = 1 * cm
    margin_y = 1.5 * cm
    gap_x = 0.4 * cm
    gap_y = 0.4 * cm  # Reducido también

    usable_width = width - (margin_x * 2)
    cols = 3
    ticket_width = (usable_width - (gap_x * (cols - 1))) / cols
    tickets_per_row = cols

    col = 0
    row = 0
    
    vendidos = Comprador.objects.select_related('ticket').order_by('-id')

    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(dark_grey)
    c.drawCentredString(width / 2, height - 30, "TICKETS SORTEO (COMPACTO)")
    
    y = height - 50 
    x = margin_x

    for cpr in vendidos:
        if (y - (row * (ticket_height + gap_y)) - ticket_height) < margin_y:
            c.showPage()
            y = height - 50
            col = 0
            row = 0
            x = margin_x

        x_curr = margin_x + col * (ticket_width + gap_x)
        y_curr = y - (row * (ticket_height + gap_y))
        center_x = x_curr + ticket_width / 2

        # --- DIBUJO ---
        c.setFillColor(colors.HexColor("#E0E0E0"))
        c.roundRect(x_curr + 2, y_curr - ticket_height - 2, ticket_width, ticket_height, 4, fill=1, stroke=0)

        c.setFillColor(colors.white)
        c.setStrokeColor(border_color)
        c.setLineWidth(1)
        c.roundRect(x_curr, y_curr - ticket_height, ticket_width, ticket_height, 4, fill=1, stroke=1)

        c.setStrokeColor(colors.HexColor("#BBBBBB"))
        c.setLineWidth(0.5)
        c.setDash(2, 2)
        c.line(x_curr + 0.3, y_curr - ticket_height + 3, x_curr + 0.3, y_curr - 3)
        c.setDash([])

        # --- CONTENIDO ---
        
        # 1. NÚMERO (MÁS GRANDE)
        c.setFillColor(honda_red)
        c.setFont("Helvetica-Bold", 18)  # Aumentado de 16 a 18
        c.drawCentredString(center_x, y_curr - 18, f"N° {cpr.ticket.numero}")

        c.setStrokeColor(honda_red)
        c.setLineWidth(1)
        c.line(x_curr + 4, y_curr - 24, x_curr + ticket_width - 4, y_curr - 24)

        # 2. NOMBRES (MÁS GRANDE)
        c.setFillColor(dark_grey)
        c.setFont("Helvetica-Bold", 11)  # Aumentado de 9 a 11
        nombres = cpr.nombres
        if len(nombres) > 22: nombres = nombres[:20] + "..."
        c.drawCentredString(center_x, y_curr - 37, nombres)

        # 3. APELLIDOS (MÁS GRANDE)
        c.setFont("Helvetica-Bold", 11)  # Aumentado de 9 a 11
        apellidos = cpr.apellidos
        if len(apellidos) > 22: apellidos = apellidos[:20] + "..."
        c.drawCentredString(center_x, y_curr - 48, apellidos)

        # 4. CELULAR (MÁS GRANDE)
        c.setFillColor(colors.HexColor("#555555"))
        c.setFont("Helvetica", 10)  # Aumentado de 9 a 10
        c.drawCentredString(center_x, y_curr - 63, f"Cel: {cpr.celular}")

        # FOOTER
        c.setFillColor(colors.HexColor("#F2F2F2"))
        c.rect(x_curr + 1, y_curr - ticket_height + 1, ticket_width - 2, 11, fill=1, stroke=0)
        c.setFillColor(honda_red)
        c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(center_x, y_curr - ticket_height + 3.5, "TICKET VENDIDO")

        col += 1
        if col >= tickets_per_row:
            col = 0
            row += 1

    c.save()
    return response

def exportar_tickets_venta_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="tickets_venta.pdf"'

    c = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # ✅ COLORES Y ESTILOS
    honda_red = colors.HexColor("#DC002E")
    dark_grey = colors.HexColor("#222222")
    badge_bg = colors.HexColor("#E0E0E0")
    border_color = colors.HexColor("#DDDDDD")

    # ✅ DIMENSIONES OPTIMIZADAS
    ticket_width = 17 * cm
    ticket_height = 7.5 * cm
    margin_x = (width - ticket_width) / 2
    margin_y = 2 * cm

    x = margin_x
    y = height - margin_y

    tickets = Ticket.objects.all().order_by('numero')

    # RUTAS (Igual que antes)
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'logo.jpg')
    p1 = os.path.join(settings.BASE_DIR, 'static', 'premio1.png')
    p2 = os.path.join(settings.BASE_DIR, 'static', 'premio2.png')
    p3 = os.path.join(settings.BASE_DIR, 'static', 'premio3.png')

    # CABECERA
    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(dark_grey)
    c.drawCentredString(width / 2, height - 40, "LISTADO OFICIAL DE TICKETS")
    
    y -= 80

    for ticket in tickets:
        if y - ticket_height < margin_y:
            c.showPage()
            y = height - margin_y - 50

        # --- FONDO Y BORDE ---
        c.setFillColor(colors.HexColor("#EAEAEA"))
        c.roundRect(x + 4, y - ticket_height - 4, ticket_width, ticket_height, 12, fill=1, stroke=0)

        c.setFillColor(colors.white)
        c.setStrokeColor(border_color)
        c.setLineWidth(1)
        c.roundRect(x, y - ticket_height, ticket_width, ticket_height, 12, fill=1, stroke=1)

        # --- MARCA DE AGUA (HONDA GIGANTE) ---
        if os.path.exists(logo_path):
            c.saveState()
            c.setFillAlpha(0.05)  # Transparencia muy alta (5% opacidad)
            # Dibujamos el logo muy grande en el centro del ticket
            # Truco: Usamos mask=None para que se mezcle, o simplemente dibujamos una imagen tenue
            # ReportLab standard no soporta opacidad de imagen nativa fácilmente sin utils complejos, 
            # pero podemos simular "marca de agua" si la imagen ya fuera clara o dibujándola antes del texto.
            # Alternativa simple: No poner imagen, poner texto "HONDA" gigante gris.
            c.setFont("Helvetica-Bold", 60)
            c.setFillColor(colors.HexColor("#F2F2F2")) # Gris muy muy claro
            c.translate(x + ticket_width/2, y - ticket_height/2)
            c.rotate(15)
            c.drawCentredString(0, -15, "HONDA")
            c.restoreState()

        # --- BARRA LATERAL (STUB) ---
        stub_width = 1.3 * cm
        c.saveState()
        p = c.beginPath()
        p.roundRect(x, y - ticket_height, ticket_width, ticket_height, 12)
        c.clipPath(p, stroke=0)
        c.setFillColor(honda_red)
        c.rect(x, y - ticket_height, stub_width, ticket_height, fill=1, stroke=0)
        
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 9)
        c.translate(x + 0.9*cm, y - ticket_height/2)
        c.rotate(90)
        c.drawCentredString(0, 0, "HONDA MOTORS 2025")
        c.restoreState()

        # LÍNEA DE CORTE
        c.setStrokeColor(colors.grey)
        c.setLineWidth(1)
        c.setDash(4, 4)
        c.line(x + stub_width, y - ticket_height + 5, x + stub_width, y - 5)
        c.setDash([])

        # --- CONTENIDO ---
        content_x = x + stub_width + 18 

        # TÍTULO PRINCIPAL
        c.setFillColor(dark_grey)
        c.setFont("Helvetica-Bold", 17) # +1 pt
        c.drawString(content_x, y - 28, "GRAN SORTEO ANUAL")

        # NÚMERO DE TICKET
        c.setFillColor(honda_red)
        c.setFont("Helvetica-Bold", 24) # +4 pts (Más grande)
        c.drawRightString(x + ticket_width - 25, y - 28, f"N° {ticket.numero}")

        # BADGES (Más grandes)
        badge_y = y - 60
        c.setFillColor(badge_bg)
        c.roundRect(content_x, badge_y - 6, 100, 22, 6, fill=1, stroke=0) # Badge más alto
        c.setFillColor(dark_grey)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(content_x + 8, badge_y, f"Cód: {ticket.codigo}")

        c.setFillColor(badge_bg)
        c.roundRect(content_x + 110, badge_y - 6, 80, 22, 6, fill=1, stroke=0)
        c.setFillColor(colors.black)
        c.drawString(content_x + 120, badge_y, f"S/ {ticket.precio}")

        # LOGO (TAMAÑO AUMENTADO)
        # Ahora 60x50 (antes 40x30)
        if os.path.exists(logo_path):
        # x + ticket_width - 100 -> Lo mueve más a la izquierda
        # y - 110 -> Lo mueve más abajo
            c.drawImage(logo_path, x + ticket_width - 100, y - 105, 80, 70, mask='auto', preserveAspectRatio=True)

        # LISTA DE PREMIOS (Texto más grande y espaciado)
        p_y = y - 100
        c.setFillColor(honda_red)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(content_x, p_y, "PREMIOS A SORTEAR:")

        c.setFillColor(dark_grey)
        c.setFont("Helvetica", 9) # +1 pt
        line_h = 13 # +3 pts separación
        c.drawString(content_x, p_y - 18, "• 1er: Honda Navi 110")
        c.drawString(content_x, p_y - 18 - line_h, "• 2do: Casco Certificado")
        c.drawString(content_x, p_y - 18 - line_h*2, "• 3er: Premio Efectivo")

        # --- IMÁGENES PREMIOS (TAMAÑO AUMENTADO) ---
        # Ahora 80x60 (antes 50x35) -> Mucho más visibles
        img_w = 80
        img_h = 60
        gap = 8 # Más espacio entre ellas
        
        # Ajustamos la base Y para que no se salgan por abajo
        base_img_y = y - ticket_height + 10 
        end_x = x + ticket_width - 20
        
        x3 = end_x - img_w
        x2 = x3 - img_w - gap
        x1 = x2 - img_w - gap

        if os.path.exists(p1):
            c.drawImage(p1, x1, base_img_y, img_w, img_h, mask='auto', preserveAspectRatio=True)
        if os.path.exists(p2):
            c.drawImage(p2, x2, base_img_y, img_w, img_h, mask='auto', preserveAspectRatio=True)
        if os.path.exists(p3):
            c.drawImage(p3, x3, base_img_y, img_w, img_h, mask='auto', preserveAspectRatio=True)

        # TEXTO LEGAL
        c.setFillColor(colors.grey)
        c.setFont("Helvetica-Oblique", 7)
        c.drawString(content_x, y - ticket_height + 8, "Sorteo supervisado por notario público.")

        y -= ticket_height + 30

    c.save()
    return response