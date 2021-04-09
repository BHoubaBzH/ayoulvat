import uuid

from django.db import models

from phonenumber_field.modelfields import PhoneNumberField

from association.models import Association

from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class AssoOrigine(models.Model):
    UUID_assoorigine = \
        models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    nom = models.CharField(max_length=50,
                           verbose_name="association repésentée par le bénévole")

    def __str__(self):
        return self.nom

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

    UUID_personne = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    # on oblige a rentrer un nom et un prenom et on retire username
    last_name = models.CharField(_('last name'), max_length=30, blank=False, unique=False)
    first_name = models.CharField(_('first name'), max_length=30, blank=False, unique=False)
    email = models.EmailField(_('email address'), unique=True)

    # on ne peut pas supprimer une asso origine tant
    # qu'une personne en fait partie
    assoorigine = models.ForeignKey(AssoOrigine,
                                primary_key=False,
                                null=True,
                                blank=True,
                                default='',
                                on_delete=models.PROTECT,
                                help_text='association pour la quelle le benevole travaille')
    role = models.CharField(max_length=50, blank=True, default='')
    genre = models.CharField(max_length=50, choices=genreListe, default=NSP)
    date_de_naissance = models.DateField(default='2000-01-01')
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
    UUID_administrateur = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
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
    UUID_organisateur = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
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
    UUID_responsable = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
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
    UUID_benevole = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    # supprime le benevole si l'entree personne est supprimee
    personne = models.OneToOneField(Personne,
                                    default='',
                                    null=True,
                                    on_delete=models.CASCADE)
    message = models.TextField(max_length=1000, blank=True, default='')

    def __str__(self):
        if not self.personne.last_name and not self.personne.first_name:
            return "{0}".format(self.personne.username)
        else:
            return "{0} {1}".format(self.personne.last_name.upper(), \
                                    self.personne.first_name.capitalize())