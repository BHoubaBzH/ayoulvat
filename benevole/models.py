import uuid

from django.db import models

from phonenumber_field.modelfields import PhoneNumberField
from colorful.fields import RGBColorField

from association.models import Association

from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class Personne(AbstractUser):
    #MIN = "MINEUR"
    HOM = "HOMME"
    FEM = "FEMME"
    NSP = "NSP"
    genreListe = [
        #(MIN, 'Mineur'),  # remplacé par un calcul sur l'age
        (HOM, 'Homme'),
        (FEM, 'Femme'),
        (NSP, 'Ne se prononce pas'),
    ]

    UUID = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    # on oblige a rentrer un nom et un prenom et on retire username
    last_name = models.CharField(_('last name'), max_length=30, blank=False, unique=False, help_text='Requis')
    first_name = models.CharField(_('first name'), max_length=30, blank=False, unique=False, help_text='Requis')
    email = models.EmailField(_('email address'), unique=True, help_text='Requis')
    role = models.CharField(max_length=50, blank=True, default='')
    genre = models.CharField(max_length=50, choices=genreListe, default=NSP, help_text='Option')
    date_de_naissance = models.DateField(null=True, default="2000-01-01", help_text='Requis')
    fixe = PhoneNumberField(null=True,
                            blank=True,
                            unique=False,
                            help_text='Option')
    portable = PhoneNumberField(null=True,
                                blank=True,
                                unique=False,  # unique=False car une personne peu etre contact pour plusieures assos
                                help_text='Option. Un numéro pour te joindre le jour J.')
    description = models.CharField(max_length=500, blank=True, default='', help_text='Option')

    def __str__(self):
        if not self.last_name and not self.first_name:
            return f"{self.username}"
        else:
            return f"{self.last_name.upper()} {self.first_name.capitalize()}"

# class abstraite utilisée par les profiles admin/orga/responsable/benevole...
class ProfileAbstract(models.Model):
    UUID = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    # supprime l objet si l'entree personne est supprimee
    personne = models.OneToOneField(Personne,
                                    default='',
                                    null=True,
                                    on_delete=models.CASCADE)
    class Meta:
        abstract = True

# paramètres specifiques administrateurs de l'asso
class ProfileAdministrateur(ProfileAbstract):
    def __str__(self):
        return f"{self.personne}"

# paramètres specifiques organisateur de l'evenement
# a coder
class ProfileOrganisateur(ProfileAbstract):
    def __str__(self):
        return f"{self.personne}"


# paramètres specifiques responsable d'equipe
# a coder
class ProfileResponsable(ProfileAbstract):
    def __str__(self):
        return f"{self.personne}"

# paramètres specifiques benevole
class ProfileBenevole(ProfileAbstract):
    message = models.TextField(max_length=1000, blank=True, default='')
    couleur = RGBColorField(default="#6610f2") 

    def __str__(self):
        return f"{self.personne} / {self.personne.email}"