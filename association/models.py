import uuid
from django.db import models
from django.utils.timezone import now
from phonenumber_field.modelfields import PhoneNumberField

from administration.models import Formule


class Association(models.Model):
    UUID = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    nom = models.CharField(max_length=50)
    adresse = models.CharField(max_length=100)
    ville = models.CharField(max_length=50)
    pays = models.CharField(max_length=50)
    code_postal = models.IntegerField()
    courriel = models.EmailField(default='')
    fixe = PhoneNumberField(null=True, blank=True,
                            unique=False)  # unique=False car une personne peu etre contact pour plusieures assos
    portable = PhoneNumberField(null=False, blank=True,
                                unique=False)  # unique=False car une personne peu etre contact pour plusieures assos
    site_web = models.URLField(blank=False, default='')
    description = models.CharField(max_length=500, blank=True, default='')
    referent = models.ForeignKey('benevole.ProfileAdministrateur',
                                       null=True,
                                       default='',
                                       related_name='admin',
                                       on_delete=models.SET_NULL,
                                       help_text='administrateur référent de l\'asso',)
    est_actif = models.BooleanField(default=False, help_text="permet de geler une asso : "
                                                             " - qui n'a pas payé"
                                                             " - supprimée, pour garder l'historique")
    date_creation = models.DateField(default=now, blank=False)
    # fait le lien avec les Administrateurs
    # Administrateurs = models.ManyToManyField('benevole.ProfileAdministrateur', related_name='Administrateur')

    def __str__(self):
        return self.nom


class Abonnement(models.Model):
    UUID = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    association = models.ForeignKey(Association,
                                    primary_key=False,
                                    default='',
                                    null=True,
                                    on_delete=models.CASCADE) # supp l'abonnement si l'asso est supprimée
    a_jour = models.BooleanField(default=False)
    date_debut = models.DateField()
    date_fin = models.DateField()
    facture_nom = models.CharField(max_length=50)
    facture_adresse = models.CharField(max_length=100)
    facture_ville = models.CharField(max_length=50)
    facture_pays = models.CharField(max_length=50, default="France")
    facture_code_postal = models.IntegerField()
    facture_courriel = models.EmailField(default='')
    description = models.CharField(max_length=500, blank=True, default='')
    # on ne peut pas suprimer un tarif/formule si un abonnement pointe dessus
    formule = models.ForeignKey(Formule,
                                   primary_key=False,
                                   default='',
                                   null=True,
                                   on_delete=models.PROTECT)

    def __bool__(self):
        return self.a_jour

class AssoPartenaire(models.Model):
    UUID = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    Association = models.ForeignKey(Association,   # les assos partenaires sont définies par asso organisatrice 
                            primary_key=False, 
                            default="None",
                            null=False,
                            blank=False,
                            on_delete=models.CASCADE,)
    nom = models.CharField(max_length=50, 
                           unique=False,
                           verbose_name="association partenaire")

    def __str__(self):
        return self.nom