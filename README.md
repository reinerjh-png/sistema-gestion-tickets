# Sistema de Gestión de Tickets de Rifa 🎟️

Aplicación web desarrollada en Django para la administración, control y venta de tickets de rifas, con generación automática de tickets en PDF listos para imprimir.

## Características
- Registro de vendedores.
- Generación automática de tickets por rango.
- Asignación de tickets a vendedores.
- Panel de administración para ver ventas.
- Control de tickets vendidos y no vendidos.
- Reporte de dinero recaudado por vendedor.
- Generación de PDF de tickets vendidos en formato mini-ticket.
- Generación de PDF de tickets de venta con:
  - Logo del negocio.
  - Número de ticket.
  - Código único generado por el sistema.
  - Precio del ticket.
  - Listos para imprimir y distribuir a los vendedores.

## 🛠️ Tecnologías utilizadas

- Python 3
- Django
- SQLite3
- HTML, CSS y JavaScript
- ReportLab / WeasyPrint (PDF)

## Instalación
1. Clona el repositorio.
2. Crea un entorno virtual: `py -m venv venv` y luego activa `venv\Scripts\activate`
3. Instala dependencias: `pip install -r requirements.txt`
4. Ejecuta las migraciones: `python manage.py makemigrations` y luego `python manage.py migrate`
5. Crea un superusuario: `python manage.py createsuperuser`
6. Inicia el servidor: `py manage.py runserver`
