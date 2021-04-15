import uuid
from django.db import models
from association.models import Association
from benevole.models import ProfileOrganisateur, ProfileResponsable, ProfileBenevole
from colorful.fields import RGBColorField


class Evenement(models.Model):
    UUID_evenement = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    # supprime evenement si asso supprimée
    association = models.ForeignKey(Association,
                                    primary_key=False,
                                    default='',
                                    on_delete=models.CASCADE)
    organisateur = models.ManyToManyField(ProfileOrganisateur,
                                          related_name='OrganisateurEvenement',
                                          blank=True,
                                          default='')
    benevole = models.ManyToManyField(ProfileBenevole,
                                      related_name='BenevolesEvenement',
                                      blank=True,
                                      default='')
    nom = models.CharField(max_length=50)
    date_debut = models.DateField()
    date_fin = models.DateField()
    site_web = models.URLField(blank=True, default='')
    editable = models.BooleanField(default=True, help_text="si non editable, l'é vènement est bloqué."
                                                           " Seul un responsable ou + peu l'éditer ou le réouvrir")
    description = models.CharField(max_length=500, blank=True, default='')
    couleur = RGBColorField(default="#0d6efd")

    def __str__(self):
        return self.nom


class Equipe(models.Model):
    UUID_equipe = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    # supprime equipe si evenement supprimé
    evenement = models.ForeignKey(Evenement,
                                  primary_key=False,
                                  unique=False,
                                  default='',
                                  null=True,
                                  on_delete=models.CASCADE)
    responsable = models.ManyToManyField(ProfileResponsable,
                                         related_name='ResponsableEquipe',
                                         blank=True,
                                         default = '')
    nom = models.CharField(max_length=50)
    responsable_valide = models.BooleanField(help_text="les responsables doivent valider les créneaux choisis")
    responsable_creer = models.BooleanField(help_text="les responsables peuvent creer des bénévoles")
    description = models.CharField(max_length=500, blank=True, default='')
    couleur = RGBColorField(default="#0d6efd")
    benevole = models.ManyToManyField(ProfileBenevole,
                                      related_name='BenevolesEquipe',
                                      blank=True,
                                      default='')
    editable = models.BooleanField(default=True, help_text="si non editable, l'équipe est bloqué."
                                                           " Seul un responsable ou + peu l'éditer ou le réouvrir")

    def __str__(self):
        return '{0} - {1}'.format(self.evenement, self.nom)


class Planning(models.Model):
    UUID_planning = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    evenement = models.ForeignKey(Evenement,
                                  primary_key=False,
                                  unique=False,
                                  default='',
                                  null=True,
                                  on_delete=models.CASCADE)
    equipe = models.ForeignKey(Equipe, primary_key=False,
                               unique=False,
                               default='',
                               null=False,
                               on_delete=models.CASCADE)
    benevole = models.ManyToManyField(ProfileBenevole,
                                      related_name='BenevolesPlanning',
                                      blank=True,
                                      default='')
    nom = models.CharField(max_length=50)
    debut = models.DateTimeField(blank=False, default='')
    fin = models.DateTimeField(blank=False, default='')
    creneaux = models.BooleanField(help_text="par créneaux fixes ou par entrée libre des bénévoles")
    ouvert_mineur = models.BooleanField(default=True,
                                        help_text='possibilité de bloquer l\'accès aux mineurs, ex : BAR')
    description = models.CharField(max_length=500, blank=True, default='')
    couleur = RGBColorField(default="#0d6efd")
    pas = models.IntegerField(default="30",blank=False,help_text="pas de reglage des creneaux en minutes: 15 / 30 / 60")
    editable = models.BooleanField(default=True, help_text="si non editable, le planning est bloqué."
                                                           " Seul un responsable ou + peu l'éditer ou le réouvrir")
    def __str__(self):
        return '{0} - {1}'.format(self.equipe, self.nom)


# reste a gérer les postes par équipe / planning
class Poste(models.Model):
    UUID_poste = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    evenement = models.ForeignKey(Evenement,
                                  primary_key=False,
                                  unique=False,
                                  blank=False,
                                  default='',
                                  null=True,
                                  on_delete=models.CASCADE)
    equipe = models.ForeignKey(Equipe, primary_key=False,
                               unique=False,
                               blank=False,
                               default='',
                               null=False,
                               on_delete=models.CASCADE)
    planning = models.ForeignKey(Planning,
                                 primary_key=False,
                                 blank=False,
                                 default='',
                                 null=False,
                                 on_delete=models.CASCADE)
    benevole = models.ManyToManyField(ProfileBenevole,
                                      related_name='BenevolesPoste',
                                      blank=True,
                                      default='',
                                      help_text='responsable de poste, ca n a surement pas de sens')
    nom = models.CharField(max_length=50)
    description = models.CharField(max_length=500, blank=True, default='')
    couleur = RGBColorField(default="#0d6efd")
    editable = models.BooleanField(default=True, help_text="si non editable, le poste est bloqué."
                                                           " Seul un responsable ou + peu l'éditer ou le réouvrir")
    def __str__(self):
        return '{0} - {1}'.format(self.planning, self.nom)


class Creneau(models.Model):
    UUID_creneau = \
        models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    evenement = models.ForeignKey(Evenement,
                                  primary_key=False,
                                  unique=False,
                                  blank=False,
                                  default='',
                                  null=True,
                                  on_delete=models.CASCADE)
    equipe = models.ForeignKey(Equipe, primary_key=False,
                               unique=False,
                               blank=False,
                               default='',
                               null=False,
                               on_delete=models.CASCADE)
    planning = models.ForeignKey(Planning,
                                 primary_key=False,
                                 blank=False,
                                 default='',
                                 null=False,
                                 on_delete=models.CASCADE)
    poste = models.ForeignKey(Poste,
                              primary_key=False,
                              blank=False,
                              default='',
                              null=False,
                              on_delete=models.CASCADE)
    benevole = models.ForeignKey(ProfileBenevole,
                                 related_name='BenevolesCreneau',
                                 null=True,
                                 blank=True,
                                 default='',
                                 on_delete=models.SET_NULL)
    nom = models.CharField(max_length=80,
                           blank=True,
                           default='',
                           help_text='le champs sera écrasé automatiquement')

    debut = models.DateTimeField(blank=False, default='')
    fin = models.DateTimeField(blank=False, default='')
    description = models.CharField(max_length=500, blank=True, default='')
    editable = models.BooleanField(default=True, help_text="si non editable, le créneau est bloqué."
                                                           " Seul un responsable ou + peu l'éditer ou le réouvrir")

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
