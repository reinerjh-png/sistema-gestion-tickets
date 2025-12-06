from django.db import models

class Vendedor(models.Model):
    nombres = models.CharField(max_length=100)
    celular = models.CharField(max_length=15)

    def __str__(self):
        return self.nombres
