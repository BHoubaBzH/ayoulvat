import uuid
from django.db import models


class Formule(models.Model):
    UUID_formule = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    nom = models.CharField(max_length=100)
    cout = models.IntegerField(default=0)
    description = models.CharField(max_length=500, blank=True, default='')

    def __str__(self):
        return self.nom


class Logs(models.Model):
    jour = models.DateField()
    heure = models.TimeField()
    log = models.CharField(max_length=250)

    def __str__(self):
        return self.log
