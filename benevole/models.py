from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import uuid

from django.db import models
from django.db.models.fields.related import ForeignKey

from phonenumber_field.modelfields import PhoneNumberField
from colorful.fields import RGBColorField

from association.models import AssoPartenaire, Association

from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _



class Personne(AbstractUser):
    MIN = "MINEUR"
    HOM = "HOMME"
    FEM = "FEMME"
    NSP = "NSP"
    genreListe = [
        (MIN, 'Mineur'),  # a remplacer a terme pour le choix par un calcul sur l'age
        (HOM, 'Homme'),
        (FEM, 'Femme'),
        (NSP, 'Ne se prononce pas'),
    ]

    UUID = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    # on oblige a rentrer un nom et un prenom et on retire username
    last_name = models.CharField(_('last name'), max_length=30, blank=False, unique=False)
    first_name = models.CharField(_('first name'), max_length=30, blank=False, unique=False)
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(max_length=50, blank=True, default='')
    genre = models.CharField(max_length=50, choices=genreListe, default=NSP)
    date_de_naissance = models.DateField(null=True, default=datetime.now()+relativedelta(years=-20))
    fixe = PhoneNumberField(null=True,
                            blank=True,
                            unique=False,
                            help_text='donnée optionnelle')
    portable = PhoneNumberField(null=False,
                                blank=False,
                                unique=False,  # unique=False car une personne peu etre contact pour plusieures assos
                                help_text='donnée obligatoire')
    description = models.CharField(max_length=500, blank=True, default='')


# paramètres specifiques administrateurs de l'asso
class ProfileAdministrateur(models.Model):
    UUID = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    # supprime l administrateur si l'entree personne est supprimee
    personne = models.OneToOneField(Personne,
                                    default='',
                                    null=True,
                                    on_delete=models.CASCADE)
    # supprime l administrateur si l'asso est supprimée, le benevole reste
    association = models.ForeignKey(Association,
                                    default='',
                                    blank=True,
                                    null=True,
                                    on_delete=models.CASCADE)
    referent = models.BooleanField(default=False)

    def __str__(self):
        if not self.personne.last_name and not self.personne.first_name:
            return "{0}".format(self.personne.username)
        else:
            return "{0} {1}".format(self.personne.last_name.upper(), \
                                    self.personne.first_name.capitalize())


# paramètres specifiques organisateur de l'evenement
class ProfileOrganisateur(models.Model):
    UUID = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    # supprime l'organisateur si l'entree personne est supprimee
    personne = models.OneToOneField(Personne,
                                    default='',
                                    null=True,
                                    on_delete=models.CASCADE)

    # pas de sens
    # evenement = models.ForeignKey('evenement.Evenement',
    #                              default='',
    #                              null=True,
    #                              on_delete=models.CASCADE)

    def __str__(self):
        if not self.personne.last_name and not self.personne.first_name:
            return "{0}".format(self.personne.username)
        else:
            return "{0} {1}".format(self.personne.last_name.upper(), \
                                    self.personne.first_name.capitalize())


# paramètres specifiques responsable d'equipe
class ProfileResponsable(models.Model):
    UUID = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    # supprime le responsable si l'entree personne est supprimee
    personne = models.OneToOneField(Personne,
                                    default='',
                                    null=True,
                                    on_delete=models.CASCADE)

    # pas de sens
    # equipe = models.ForeignKey('evenement.Equipe',
    #                           default='',
    #                           null=True,
    #                           on_delete=models.CASCADE)

    def __str__(self):
        if not self.personne.last_name and not self.personne.first_name:
            return "{0}".format(self.personne.username)
        else:
            return "{0} {1}".format(self.personne.last_name.upper(), \
                                    self.personne.first_name.capitalize())


# paramètres specifiques benevole
class ProfileBenevole(models.Model):
    UUID = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    # supprime le benevole si l'entree personne est supprimee
    personne = models.OneToOneField(Personne,
                                    default='',
                                    null=True,
                                    on_delete=models.CASCADE)
    message = models.TextField(max_length=1000, blank=True, default='')
    couleur = RGBColorField(default="#6610f2")

    # on ne peut pas supprimer une asso origine tant
    # qu'une personne en fait partie, le bénévole choisi son asso partenaire
    assopartenaire = models.ForeignKey(AssoPartenaire,
                                    primary_key=False,
                                    null=True,
                                    blank=True,
                                    default='',
                                    on_delete=models.PROTECT,
                                    help_text='associations partenaires de l evenement')
    def __str__(self):
        return "{0} {1}".format(self.personne.last_name.upper(), self.personne.first_name.capitalize())