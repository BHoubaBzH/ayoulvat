import uuid

from django.contrib.auth.models import User
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from evenement.models import Planning, Poste


class Origine(models.Model):
    UUID_origine = \
        models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    nom = models.CharField(max_length=50)

    def __str__(self):
        return self.nom


class ProfilePersonne(models.Model):
    MIN = "MINEUR"
    HOM = "HOMME"
    FEM = "FEMME"
    NSP = "NSP"
    genreListe = [
        (MIN, 'Mineur'), # a remplacer a terme pour le choix par un calcul sur l'age
        (HOM, 'Homme'),
        (FEM, 'Femme'),
        (NSP, 'Ne se prononce pas'),
    ]
    # La liaison OneToOne vers le modèle User
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    UUID_personne = \
        models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    UUID_origine = \
        models.ForeignKey(Origine, primary_key=False, blank=True, default='', on_delete=models.DO_NOTHING)
    role = models.CharField(max_length=50, blank=True, default='')
    genre = models.CharField(max_length=50,choices=genreListe,default=NSP)
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

    def __str__(self):
        return "{0} {1}".format(self.user.last_name.upper(), self.user.first_name.capitalize())


class Creneau(models.Model):
    UUID_creneau = \
        models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    UUID_planning = \
        models.ForeignKey(Planning, primary_key=False, blank=False, default='', on_delete=models.DO_NOTHING)
    UUID_personne = \
        models.ForeignKey(ProfilePersonne, \
                          primary_key=False, \
                          null=True, \
                          blank=True, \
                          default='', \
                          on_delete=models.DO_NOTHING)
    nom = models.CharField(max_length=80,  blank=True, default='')
    debut = models.DateTimeField(blank=False, default='')
    fin = models.DateTimeField(blank=False, default='')
    description = models.CharField(max_length=500, blank=True, default='')

    # surcharge la methode save pour mettre un nom automatiquement
    def save(self, *args, **kwargs):
        self.nom = '{0}_{1}_{2}'.format( \
            str(self.UUID_planning).replace(' ',''), \
            self.debut.strftime('%H-%M'), \
            self.fin.strftime('%H-%M'))
        super(Creneau, self).save(*args, **kwargs)

    def __str__(self):
        return self.nom
