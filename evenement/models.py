import uuid
from django.db import models
from association.models import Association


class Evenement(models.Model):
    UUID_evenement = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    UUID_association = models.ForeignKey(Association, primary_key=False, on_delete=models.CASCADE)
    nom = models.CharField(max_length=50)
    date_debut = models.DateField()
    date_fin = models.DateField()
    site_web = models.URLField()
    editable = models.BooleanField(help_text="inscription ouvertes ou non")
    description = models.CharField(max_length=500, blank=True, default='')

    def __str__(self):
        return self.nom


class Equipe(models.Model):
    UUID_equipe = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    UUID_evenement = models.ForeignKey(Evenement, primary_key=False, on_delete=models.CASCADE)
    nom = models.CharField(max_length=50)
    responsable_valide = models.BooleanField(help_text="les responsables doivent valider les créneaux choisis")
    responsable_creer = models.BooleanField(help_text="les responsables peuvent creer des bénévoles")
    description = models.CharField(max_length=500, blank=True, default='')

    def __str__(self):
        return self.nom


class Planning(models.Model):
    UUID_planning = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    UUID_equipe = models.ForeignKey(Equipe, primary_key=False, on_delete=models.CASCADE)
    nom = models.CharField(max_length=50)
    debut = models.DateTimeField()
    fin = models.DateTimeField()
    creneaux = models.BooleanField(help_text="par créneaux fixes ou par entrée libre des bénévoles")
    description = models.CharField(max_length=500, blank=True, default='')

    def __str__(self):
        return self.nom
