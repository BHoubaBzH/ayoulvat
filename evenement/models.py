import uuid
from django.db import models
from association.models import Association
from benevole.models import ProfileBenevole, ProfileOrganisateur, ProfileResponsable


class Evenement(models.Model):
    UUID_evenement = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    UUID_association = models.ForeignKey(Association, primary_key=False, on_delete=models.CASCADE)
    UUID_benevole = models.ManyToManyField(ProfileOrganisateur,
                                           related_name='Organisateur')
    nom = models.CharField(max_length=50)
    date_debut = models.DateField()
    date_fin = models.DateField()
    site_web = models.URLField(blank=True, default='')
    editable = models.BooleanField(help_text="inscription ouvertes ou non")
    description = models.CharField(max_length=500, blank=True, default='')

    def __str__(self):
        return self.nom


class Equipe(models.Model):
    UUID_equipe = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    UUID_evenement = models.ForeignKey(Evenement, primary_key=False, unique=False, on_delete=models.CASCADE)
    UUID_benevole = models.ManyToManyField(ProfileResponsable,
                                           related_name='Responsable')
    nom = models.CharField(max_length=50)
    responsable_valide = models.BooleanField(help_text="les responsables doivent valider les créneaux choisis")
    responsable_creer = models.BooleanField(help_text="les responsables peuvent creer des bénévoles")
    description = models.CharField(max_length=500, blank=True, default='')

    def __str__(self):
        return '{0} - {1}'.format(self.UUID_evenement, self.nom)


class Planning(models.Model):
    UUID_planning = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    UUID_equipe = models.ForeignKey(Equipe, primary_key=False, on_delete=models.CASCADE)
    nom = models.CharField(max_length=50)
    debut = models.DateTimeField()
    fin = models.DateTimeField()
    creneaux = models.BooleanField(help_text="par créneaux fixes ou par entrée libre des bénévoles")
    ouvert_mineur = models.BooleanField(default=True,
                                        help_text='possibilité de bloquer l\'accès aux mineurs, ex : BAR')
    description = models.CharField(max_length=500, blank=True, default='')

    def __str__(self):
        return '{0} - {1}'.format(self.UUID_equipe, self.nom)


# reste a gérer les postes par équipe / planning
class Poste(models.Model):
    UUID_poste = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    planning = models.ForeignKey(Planning, primary_key=False, on_delete=models.CASCADE)
    nom = models.CharField(max_length=50)

    def __str__(self):
        return '{0} - {1}'.format(self.planning, self.nom)


class Creneau(models.Model):
    UUID_creneau = \
        models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    poste = \
        models.ForeignKey(Poste, primary_key=False, blank=False, default='', on_delete=models.CASCADE)
    nom = models.CharField(max_length=80,
                           blank=True,
                           default='',
                           help_text='laisser vide, le champs sera rempli automatiquement')
    UUID_benevole = models.OneToOneField(ProfileBenevole,
                                         null=True,
                                         default='',
                                         primary_key=False,
                                         on_delete=models.DO_NOTHING)
    debut = models.DateTimeField(blank=False, default='')
    fin = models.DateTimeField(blank=False, default='')
    description = models.CharField(max_length=500, blank=True, default='')

    class Meta:
        verbose_name_plural = "Creneaux"

    # surcharge la methode save pour mettre un nom automatiquement
    def save(self, *args, **kwargs):
        self.nom = '{0}_{1}_{2}'.format(
            str(self.poste).replace(' ', ''),  # retire les espaces
            self.debut.strftime('%H-%M'),
            self.fin.strftime('%H-%M')
        )
        super(Creneau, self).save(*args, **kwargs)

    def __str__(self):
        return self.nom
