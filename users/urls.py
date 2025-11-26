from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('alumnos/crear/', views.crear_alumno, name='crear_alumno'),
    path('alumnos/editar/<int:pk>/', views.editar_alumno, name='editar_alumno'),
    path('alumnos/eliminar/<int:pk>/', views.eliminar_alumno, name='eliminar_alumno'),
    path('alumnos/enviar-pdf/<int:pk>/', views.enviar_pdf_alumno, name='enviar_pdf_alumno'),
    path('alumnos/descargar-pdf/<int:pk>/', views.descargar_pdf_alumno, name='descargar_pdf_alumno'),
]