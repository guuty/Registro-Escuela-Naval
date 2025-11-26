from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER


def generar_pdf_alumno(alumno):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch)
    
    # Colores navales
    azul_marino = HexColor('#0a1628')
    dorado = HexColor('#d4af37')
    azul_naval = HexColor('#1a3a5c')
    
    # Estilos
    styles = getSampleStyleSheet()
    
    titulo_style = ParagraphStyle(
        'TituloNaval',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=azul_marino,
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    subtitulo_style = ParagraphStyle(
        'SubtituloNaval',
        parent=styles['Normal'],
        fontSize=14,
        textColor=azul_naval,
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    normal_style = ParagraphStyle(
        'NormalNaval',
        parent=styles['Normal'],
        fontSize=12,
        textColor=azul_marino,
        spaceAfter=10
    )
    
    # Contenido del PDF
    elementos = []
    
    # Encabezado
    elementos.append(Paragraph("⚓ ESCUELA NAVAL ⚓", titulo_style))
    elementos.append(Paragraph("Ficha de Registro de Cadete", subtitulo_style))
    elementos.append(Spacer(1, 20))
    
    # Tabla con datos del alumno
    datos = [
        ['Campo', 'Información'],
        ['Nombre', alumno.nombre],
        ['Apellido', alumno.apellido],
        ['Correo Naval', alumno.email],
        ['Edad', f'{alumno.edad} años'],
        ['División', alumno.carrera],
        ['Fecha de Registro', alumno.fecha_registro.strftime('%d/%m/%Y %H:%M')],
    ]
    
    tabla = Table(datos, colWidths=[2*inch, 4*inch])
    tabla.setStyle(TableStyle([
        # Encabezado de tabla
        ('BACKGROUND', (0, 0), (-1, 0), azul_marino),
        ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#ffffff')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        
        # Cuerpo de tabla
        ('BACKGROUND', (0, 1), (0, -1), HexColor('#f0f0f0')),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 1), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('TEXTCOLOR', (0, 1), (-1, -1), azul_marino),
        
        # Bordes
        ('GRID', (0, 0), (-1, -1), 1, dorado),
        ('LINEBELOW', (0, 0), (-1, 0), 2, dorado),
        
        # Padding
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    elementos.append(tabla)
    elementos.append(Spacer(1, 40))
    
    # Pie de página
    pie_style = ParagraphStyle(
        'PieNaval',
        parent=styles['Normal'],
        fontSize=10,
        textColor=azul_naval,
        alignment=TA_CENTER
    )
    elementos.append(Paragraph("— Honor, Valor y Lealtad —", pie_style))
    elementos.append(Spacer(1, 10))
    elementos.append(Paragraph("Documento generado por el Sistema de Registro Naval", pie_style))
    
    # Construir PDF
    doc.build(elementos)
    buffer.seek(0)
    
    return buffer