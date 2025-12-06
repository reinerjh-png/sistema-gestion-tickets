from django.contrib import admin
from .models import Ticket, Comprador


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('numero', 'estado', 'precio', 'vendedor')
    search_fields = ('numero',)   # ✅ BUSCAR POR NÚMERO DE TICKET
    list_filter = ('estado', 'vendedor')
    ordering = ('numero',)


@admin.register(Comprador)
class CompradorAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'apellidos', 'dni', 'celular', 'ticket')
    search_fields = ('dni', 'nombres', 'apellidos')
