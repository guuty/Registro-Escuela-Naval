from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from .forms import RegisterForm, AlumnoForm
from .models import Alumno
from .utils import generar_pdf_alumno
from django.http import HttpResponse

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
    pdf_buffer = generar_pdf_alumno(alumno)
    
    # Crear email con adjunto
    try:
        email = EmailMessage(
            subject=f'📋 Ficha de Cadete: {alumno.nombre} {alumno.apellido}',
            body=f'Estimado/a,\n\nAdjunto encontrará la ficha del cadete {alumno.nombre} {alumno.apellido}.\n\n— Escuela Naval —\nHonor, Valor y Lealtad',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[request.user.email],
        )
        
        # Adjuntar PDF
        email.attach(
            f'ficha_cadete_{alumno.nombre}_{alumno.apellido}.pdf',
            pdf_buffer.getvalue(),
            'application/pdf'
        )
        
        # Enviar con timeout
        email.send(fail_silently=False)
        messages.success(request, f'📧 PDF enviado exitosamente a {request.user.email}')
    except Exception as e:
        messages.warning(request, f'⚠️ No se pudo enviar el correo. El PDF se generó correctamente.')
    
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