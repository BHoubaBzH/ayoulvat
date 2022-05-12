import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls.base import set_urlconf
from association.models import AssoPartenaire, Association
from benevole.models import ProfileOrganisateur, ProfileResponsable, ProfileBenevole
from colorful.fields import RGBColorField
from datetime import date


class Evenement(models.Model):
    # défini le format de sauvegarde de la vignette
    def upload_dir_vignette(self, filename):
        nom_propre = [character for character in str(self.nom) if character.isalnum()]
        nom_propre = "".join(nom_propre)
        return f'{nom_propre}/{self.debut.year}/{filename}'

    UUID = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    # supprime evenement si asso supprimée
    association = models.ForeignKey(Association,
                                    primary_key=False,
                                    default='',
                                    on_delete=models.CASCADE)
    assopartenaire = models.ManyToManyField(AssoPartenaire,
                                    primary_key=False,
                                    blank=True,
                                    default='',
                                    help_text='associations partenaires de \'évèmenement ')
    organisateur = models.ManyToManyField(ProfileOrganisateur,
                                    related_name='OrganisateurEvenement',
                                    blank=True,
                                    default='')
    benevole = models.ManyToManyField(ProfileBenevole,
                                    related_name='BenevolesEvenement',
                                    blank=True,
                                    default='les benevoles peuvent s inscrire a l envenement',
                                    through='evenement_benevole_assopart')
    nom = models.CharField(max_length=50)
    debut = models.DateTimeField(blank=False, default='')
    fin = models.DateTimeField(blank=False, default='')
    inscription_debut = models.DateField( default= date.today, blank=True, help_text="date à partir de laquelle les inscriptions des bénévoles sont possibles")
    inscription_fin = models.DateField(default= date.today, blank=True, help_text="date à partir de laquelle les inscriptions des bénévoles sont closes")
    editable = models.BooleanField(default=True, help_text="si éditable, l'évènement est ouvert à tous. Sinon, il n'est pas modifiable")
    site_web = models.URLField(blank=True, default='')
    description = models.TextField(max_length=2000, blank=True, default='')
    commentaire = models.TextField(max_length=500, blank=True, default='', help_text="texte expliquant ce que le bénévole peut demander par courriel")
    courriel_organisateur = models.EmailField(default='', help_text="courriel accessible aux bénévoles en bas de page", blank=True)
    vignette = models.ImageField(upload_to=upload_dir_vignette, blank=True)
    couleur = RGBColorField(default="#6610f2")

    def __str__(self):
        return self.nom

class evenement_benevole_assopart(models.Model):
    """
        remplace la table M2M  evenement_benevole créée par defaut.
        permet de lier evenement / benevole / asso partenaire
    """
    id = models.AutoField(primary_key=True, editable=False, unique=True)
    evenement = models.ForeignKey(Evenement, on_delete=models.CASCADE)
    profilebenevole = models.ForeignKey(ProfileBenevole, on_delete=models.CASCADE)
    asso_part = models.ForeignKey(AssoPartenaire, default='', blank=True, null=True, on_delete=models.SET_NULL) 

    def __str__(self):
        return f'{self.evenement} - {self.asso_part} - {self.profilebenevole}'

class Equipe(models.Model):
    UUID = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
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
    description = models.TextField(max_length=1000, blank=True, default='')
    couleur = RGBColorField(default="#e91e63")
    seuil1 = models.IntegerField(default=50,
                                validators=[
                                    MinValueValidator(1),
                                    MaxValueValidator(100)],
                                help_text="pourcentage à partir du quel la stat du dashboard devient jaune")
    seuil2 = models.IntegerField(default=80,
                                validators=[
                                    MinValueValidator(1),
                                    MaxValueValidator(100)],    
                                help_text="pourcentage à partir du quel la stat du dashboard devient verte")
    benevole = models.ManyToManyField(ProfileBenevole,
                                      related_name='BenevolesEquipe',
                                      blank=True,
                                      default='les benevoles peuvent s inscrire a l equipe')
    editable = models.BooleanField(default=True, help_text="si éditable, les plannings de l'équipe sont modifiables."
                                                           " pas encore implémenté")

    def __str__(self):
        return f'{self.evenement} - {self.nom}'


class Planning(models.Model):
    class PasMinute(models.IntegerChoices):
        quinze = 15
        trente = 30
        heure = 60

    class CreneauMoyen(models.IntegerChoices):
        une_heure = 60
        une_heure_trente = 90
        deux_heures = 120
        deux_heures_trente = 150
        trois_heures = 180
        trois_heures_trente = 210
        quatre_heures = 240

    UUID = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
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
                                      default='les benevoles peuvent s inscrire au planning')
    nom = models.CharField(max_length=50)
    debut = models.DateTimeField(blank=False, default='')
    fin = models.DateTimeField(blank=False, default='')
    creneaux = models.BooleanField(help_text="par créneaux fixes ou par entrée libre des bénévoles")
    ouvert_mineur = models.BooleanField(default=True,
                                        help_text='possibilité de bloquer l\'accès aux mineurs, ex : BAR')
    description = models.CharField(max_length=500, blank=True, default='')
    couleur = RGBColorField(default="#6610f2")
    pas = models.PositiveSmallIntegerField(choices=PasMinute.choices,blank=False, default=30,
                                           help_text="pas de reglage des creneaux en minutes: 15 / 30 / 60")
    seuil1 = models.IntegerField(default=50,
                                validators=[
                                    MinValueValidator(0),
                                    MaxValueValidator(100)],
                                help_text="pourcentage à partir du quel la stat du dashboard devient jaune")
    seuil2 = models.IntegerField(default=80,
                                validators=[
                                    MinValueValidator(0),
                                    MaxValueValidator(100)],    
                                help_text="pourcentage à partir du quel la stat du dashboard devient verte")
    creneau_moyen = models.PositiveSmallIntegerField(choices=CreneauMoyen.choices,blank=False, default=120,
                                           help_text="duree classique d'un créneau en minutes")
    editable = models.BooleanField(default=True, help_text="si éditable, les postes du planning sont ouverts."
                                                           " pas encore implémenté")
    def __str__(self):
        return '{0} - {1}'.format(self.equipe, self.nom)


# reste a gérer les postes par équipe / planning
class Poste(models.Model):
    UUID = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
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
    nom = models.CharField(max_length=100)
    description = models.TextField(max_length=500, blank=True, default='')
    couleur = RGBColorField(default="#0d6efd")
    ouvert = models.BooleanField(default=True, help_text="si sélectionné, Les créneaux sont ouverts aux bénévoles."
                                                           " Sinon les créneaux ne sont disponibles qu'aux responsables.")
    ouvert_mineur = models.BooleanField(default=True,
                                        help_text='si sélectionné, les mineurs peuvent s\'inscrire à ce poste')
    def __str__(self):
        return '{0} - {1}'.format(self.planning, self.nom)

# creneau model : stocke les creneau de l'evenement et les dispos de benevoles
class Creneau(models.Model):
    class Type(models.TextChoices):
        creneau = "creneau"
        benevole = "benevole"

    UUID = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
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
                              blank=True, # peut etre nul pour les benevole
                              default='',
                              null=True,
                              on_delete=models.CASCADE)
    benevole = models.ForeignKey(ProfileBenevole,
                                 related_name='BenevolesCreneau',
                                 primary_key=False,
                                 null=True,
                                 blank=True,
                                 default='',
                                 on_delete=models.SET_NULL)
    nom = models.CharField(max_length=200,
                           blank=True,
                           default='',
                           help_text='le champs sera écrasé automatiquement')

    debut = models.DateTimeField(blank=False, default='')
    fin = models.DateTimeField(blank=False, default='')
    description = models.TextField(max_length=500, blank=True, default='')
    editable = models.BooleanField(default=True, help_text="si editable, le créneau n'est pas bloqué."
                                                            " pas encore implémenté")
    valide_present = models.BooleanField(blank=True, default=False, help_text="à valider si le bénévole s'est bien présenté")
    type = models.CharField(choices=Type.choices,
                            max_length=50,
                            blank=False,
                            default="creneau",
                            help_text="creneau ou dispos de bénévole")

    class Meta:
        verbose_name_plural = "Creneaux"

    # surcharge la methode save pour mettre un nom automatiquement
    def save(self, *args, **kwargs):
        if self.type == "creneau":
            nom1 = str(self.poste.nom).replace(' ', '')  # retire les espaces
            nom2 = str(self.planning.nom).replace(' ', '')  # retire les espaces
        elif self.type == "benevole":
            nom1 = str(self.benevole)\
                       .replace(' ', '-')\

        else:
            nom1 = "error"
            nom2 = "error"
        self.nom = '{}_{}_{}_{}'.format(
            nom1,
            nom2,
            self.debut.strftime('%H-%M'),
            self.fin.strftime('%H-%M')
        )[-50:]# la string ne peut pas faire plus de 50 char
        super(Creneau, self).save(*args, **kwargs)

    def __str__(self):
        return self.nom
