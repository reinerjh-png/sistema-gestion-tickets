from django.contrib import admin
from django.urls import path, include
from tickets import views

urlpatterns = [
    path('', views.bienvenida, name='bienvenida'),
    path('admin/', admin.site.urls),
    path('tickets/', include('tickets.urls')),
]
