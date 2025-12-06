from django import forms
from vendedor.models import Vendedor
from .models import Comprador

class GenerarTicketsForm(forms.Form):
    numero_inicial = forms.IntegerField(label="Número inicial")
    numero_final = forms.IntegerField(label="Número final")
    precio = forms.DecimalField(label="Precio del ticket", max_digits=8, decimal_places=2)

class RepartirTicketsForm(forms.Form):
    numero_inicio = forms.IntegerField(label="Desde el número")
    numero_fin = forms.IntegerField(label="Hasta el número")
    vendedor = forms.ModelChoiceField(queryset=Vendedor.objects.all())

class LoginTicketForm(forms.Form):
    numero = forms.IntegerField(label="Número de Ticket")
    codigo = forms.CharField(label="Código")

class RegistrarCompradorForm(forms.ModelForm):
    class Meta:
        model = Comprador
        fields = ['nombres', 'apellidos', 'dni', 'celular', 'direccion']
