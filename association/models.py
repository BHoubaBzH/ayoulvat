import uuid
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.datetime_safe import date
from django.utils.timezone import now
from phonenumber_field.modelfields import PhoneNumberField
from administration.models import Formule
from django.contrib.auth.models import User


class Association(models.Model):
    UUID_association = \
        models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    nom = models.CharField(max_length=50)
    adresse = models.CharField(max_length=100)
    ville = models.CharField(max_length=50)
    code_postal = models.IntegerField()
    courriel = models.EmailField(default='')
    fixe = PhoneNumberField(null=True, blank=True,
                            unique=False)  # unique=False car une personne peu etre contact pour plusieures assos
    portable = PhoneNumberField(null=False, blank=True,
                                unique=False)  # unique=False car une personne peu etre contact pour plusieures assos
    site_web = models.URLField(blank=False, default='')
    description = models.CharField(max_length=500, blank=True, default='')
    # attention : l'admin unique de l'asso ne pourra pas etre vide plus tard et contiendra le UUID de l'admin
    administrateur = models.CharField(max_length=500,
                                      blank=True,
                                      default='',
                                      help_text="attention : l'admin unique de l'asso ne pourra pas etre "
                                                "vide plus tard et contiendra la FK vers l'admin")
    est_actif = models.BooleanField(default=False)  # permet de geler une asso qui n'a pas payé par exemple
    date_creation = models.DateField(default=now, blank=False)
    # fait le lien avec les gestionnaires
    # Gestionnaires = models.ManyToManyField('benevole.ProfileGestionnaire', related_name='Gestionnaire')

    def __str__(self):
        return self.nom


class Abonnement(models.Model):
    UUID_abonnement = \
        models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
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
    facture_code_postal = models.IntegerField()
    facture_courriel = models.EmailField(default='')
    description = models.CharField(max_length=500, blank=True, default='')
    # on ne peut pas suprimer un tarif/formule si un abonnement pointe dessus
    formule = models.OneToOneField(Formule,
                                   primary_key=False,
                                   default='',
                                   null=True,
                                   on_delete=models.PROTECT)

    def __bool__(self):
        return self.a_jour


''' passé dans app benevole
# classe de surcharge sur le model user avec un profile
class ProfileGestionnaire(models.Model):
    # La liaison OneToOne vers le modèle User
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    UUID_gestionnaire = \
        models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    role = models.CharField(max_length=50, blank=True, default='')
    genre = models.CharField(max_length=50, blank=True, default='')
    date_de_naissance = models.DateField(default='2000-01-01')
    fixe = PhoneNumberField(null=True,
                            blank=True,
                            unique=False,
                            help_text='donnée optionnelle')
    # unique=False car une personne peu etre contact pour plusieures assos
    portable = PhoneNumberField(null=False,
                                blank=False,
                                unique=False,
                                help_text='donnée obligatoire')
    description = models.CharField(max_length=500, blank=True, default='')

    def __str__(self):
        return "{0} {1}".format(self.user.last_name.upper(), self.user.first_name.capitalize())


# Basically we are hooking the create_or_update_user_profile method to the User model
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        ProfileGestionnaire.objects.create(user=instance)
    # instance.profile.save()
'''

