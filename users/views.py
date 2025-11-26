from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from .forms import RegisterForm, AlumnoForm
from .models import Alumno
from .utils import generar_pdf_alumno
from django.http import HttpResponse
import socket 



def home(request):
    return render(request, 'users/home.html')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Enviar correo de bienvenida
            send_mail(
                subject='¡Bienvenido a la Escuela Naval!',
                message=f'Hola {user.username},\n\nGracias por alistarte en nuestra Escuela Naval.\n\n¡Bienvenido a bordo!\n\n— Honor, Valor y Lealtad —',
                from_email=settings.EMAIL_HOST_USER if hasattr(settings, 'EMAIL_HOST_USER') else 'noreply@escuelanaval.com',
                recipient_list=[user.email],
                fail_silently=True,
            )
            
            messages.success(request, '¡Te has alistado exitosamente! Ya puedes embarcar.')
            return redirect('login')
    else:
        form = RegisterForm()
    
    return render(request, 'users/register.html', {'form': form})


@login_required
def dashboard(request):
    alumnos = Alumno.objects.filter(usuario=request.user)
    return render(request, 'users/dashboard.html', {'alumnos': alumnos})


@login_required
def crear_alumno(request):
    if request.method == 'POST':
        form = AlumnoForm(request.POST)
        if form.is_valid():
            alumno = form.save(commit=False)
            alumno.usuario = request.user
            alumno.save()
            
            # Enviar notificación al profesor
            try:
                send_mail(
                    subject=f'Nuevo Cadete Registrado: {alumno.nombre} {alumno.apellido}',
                    message=f'Se ha registrado un nuevo cadete:\n\nNombre: {alumno.nombre} {alumno.apellido}\nDNI: {alumno.dni}\nUsuario: {request.user.username}\n\n— Escuela Naval —',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['ematevez@gmail.com'],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Error enviando email: {e}")
            
            messages.success(request, '¡Cadete registrado exitosamente!')
            return redirect('dashboard')
    else:
        form = AlumnoForm()
    
    return render(request, 'users/crear_alumno.html', {'form': form})


@login_required
def editar_alumno(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        form = AlumnoForm(request.POST, instance=alumno)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Datos del cadete actualizados!')
            return redirect('dashboard')
    else:
        form = AlumnoForm(instance=alumno)
    
    return render(request, 'users/editar_alumno.html', {'form': form, 'alumno': alumno})


@login_required
def eliminar_alumno(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        alumno.delete()
        messages.success(request, '¡Cadete dado de baja exitosamente!')
        return redirect('dashboard')
    
    return render(request, 'users/eliminar_alumno.html', {'alumno': alumno})

@login_required
def enviar_pdf_alumno(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk, usuario=request.user)
    
    # Generar PDF
    try:
        pdf_buffer = generar_pdf_alumno(alumno)
    except Exception as e:
        messages.error(request, f'Error generando PDF: {str(e)}')
        return redirect('dashboard')
    
    # Intentar enviar email con múltiples timeouts
    try:
        import socket
        
        # Timeout más largo
        socket.setdefaulttimeout(120)
        
        email = EmailMessage(
            subject=f'📋 Ficha de Cadete: {alumno.nombre} {alumno.apellido}',
            body=f'Estimado/a,\n\nAdjunto encontrará la ficha del cadete {alumno.nombre} {alumno.apellido}.\n\n— Escuela Naval —\nHonor, Valor y Lealtad',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[request.user.email],
        )
        
        email.attach(
            f'ficha_cadete_{alumno.nombre}_{alumno.apellido}.pdf',
            pdf_buffer.getvalue(),
            'application/pdf'
        )
        
        # Intentar enviar con timeout explícito
        from django.core.mail import get_connection
        connection = get_connection(
            timeout=120,
            fail_silently=False
        )
        
        email.connection = connection
        email.send()
        
        messages.success(request, f'📧 PDF enviado exitosamente a {request.user.email}')
        
    except socket.timeout:
        messages.warning(request, '⏱️ El envío está tardando. El email llegará en unos minutos.')
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error enviando email: {str(e)}", exc_info=True)
        messages.warning(request, f'⚠️ El PDF se generó pero no se pudo enviar en este momento. Intenta de nuevo más tarde.')
    
    return redirect('dashboard')

@login_required
def descargar_pdf_alumno(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk, usuario=request.user)
    
    # Generar PDF
    pdf_buffer = generar_pdf_alumno(alumno)
    
    # Crear respuesta HTTP con el PDF
    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ficha_cadete_{alumno.nombre}_{alumno.apellido}.pdf"'
    
    return response