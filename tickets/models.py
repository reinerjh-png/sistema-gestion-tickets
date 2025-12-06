from django.db import models
from vendedor.models import Vendedor
import random
import string

def generar_codigo():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

class Ticket(models.Model):
    numero = models.IntegerField(unique=True)
    codigo = models.CharField(max_length=10, default=generar_codigo)
    precio = models.DecimalField(max_digits=8, decimal_places=2)

    ESTADO_CHOICES = [
        ('DISPONIBLE', 'Disponible'),
        ('ASIGNADO', 'Asignado'),
        ('VENDIDO', 'Vendido'),
    ]

    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='DISPONIBLE')
    vendedor = models.ForeignKey(Vendedor, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'Ticket {self.numero}'

class Comprador(models.Model):
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    dni = models.CharField(max_length=15)
    celular = models.CharField(max_length=15)
    direccion = models.CharField(max_length=200)

    def __str__(self):
        return self.nombres


