from django.db import models
from django.contrib.auth.models import User


class Alumno(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alumnos')
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField()
    edad = models.PositiveIntegerField()
    carrera = models.CharField(max_length=100)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_registro']

    def __str__(self):
        return f'{self.nombre} {self.apellido}'
# Create your models here.
