from django.contrib import admin
from .models import Vendedor
from tickets.models import Ticket

class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 0
    fields = ('numero', 'estado')
    readonly_fields = ('numero', 'estado')
    can_delete = False
    show_change_link = True


@admin.register(Vendedor)
class VendedorAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'celular')
    search_fields = ('nombres', 'celular')
    inlines = [TicketInline]
