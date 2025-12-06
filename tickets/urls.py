from django.urls import path
from . import views

urlpatterns = [
    path('generar/', views.generar_tickets, name='generar_tickets'),
    path('repartir/', views.repartir_tickets, name='repartir_tickets'),
    path('login-ticket/', views.login_ticket, name='login_ticket'),
    path('registrar/<int:ticket_id>/', views.registrar_comprador, name='registrar_comprador'),
    path('reporte/', views.reporte_general, name='reporte_general'),
    path('reporte-detallado/', views.reporte_detallado, name='reporte_detallado'),
    path('exportar-pdf/', views.exportar_reporte_pdf, name='exportar_reporte_pdf'),
    path('exportar-tickets-venta/', views.exportar_tickets_venta_pdf, name='exportar_tickets_venta'),
]
