import uuid

from django.db.backends.utils import logger
from django.contrib.auth.models import Group
from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver


##########################################################
# definition de nos groupes
##########################################################
admi = 'ADMINISTRATEUR'  # administrateur d'asso
orga = 'ORGANISATEUR'  # organisateur d'evenement
resp = 'RESPONSABLE'  # responsable d'equipe
bene = 'BENEVOLE'  # bénévole affecté aux creneaux

groupe_liste = [
    (admi, 'Administrateur'),
    (orga, 'Organisateur'),
    (resp, 'Responsable'),
    (bene, 'Benevole'),
]

##########################################################

class Formule(models.Model):
    UUID = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    nom = models.CharField(max_length=100)
    cout = models.IntegerField(default=0)
    description = models.CharField(max_length=500, blank=True, default='')

    def __str__(self):
        return self.nom


class Logs(models.Model):
    UUID = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    jour = models.DateField()
    heure = models.TimeField()
    log = models.CharField(max_length=500)

    def __str__(self):
        return self.log

# crée nos groupes à la fin de la migration, grace au hook
# on crée également les droits affectés aux groupes
@receiver(post_migrate)
def init_groups(sender, **kwargs):
    for code_quadri, nom in groupe_liste:
        # on cree les groupes
        Group.objects.get_or_create(name=nom)
