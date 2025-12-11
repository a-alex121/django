from django.db import models

class Categorie(models.Model):
    nume_categorie = models.CharField(max_length=50, unique=True)
    descriere = models.TextField(null=True)

    def __str__(self):
        return self.nume_categorie