import uuid

from django.db.backends.utils import logger
from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from association.models import Association


class Origine(models.Model):
    UUID_origine = \
        models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    nom = models.CharField(max_length=50)

    def __str__(self):
        return self.nom


class ProfileBenevole(models.Model):
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
    user = models.OneToOneField(User, on_delete=models.CASCADE) # supprime ce benevole si le user est supprimé
    UUID_benevole = \
        models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    # on ne peut pas supprimer une asso origine tant
    # qu'un bénévole en fait partie
    origine = models.ForeignKey(Origine,
                                primary_key=False,
                                null=True,
                                blank=True,
                                default='',
                                on_delete=models.PROTECT)
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
        if not self.user.last_name and not self.user.first_name :
            return "{0}".format(self.user.username)
        else:
            return "{0} {1}".format(self.user.last_name.upper(), self.user.first_name.capitalize())


# paramètres specifiques gestionnaires de l'asso
class ProfileGestionnaire(models.Model):
    UUID_gestionnaire = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    # supprime le gestionnaire si l'entree benevole est supprimee
    benevole = models.OneToOneField(ProfileBenevole,
                                    default='',
                                    null=True,
                                    on_delete=models.CASCADE)
    # supprime le gestionnaire si l'asso est supprimée, le benevole reste
    association = models.ForeignKey(Association,
                                    default='',
                                    null=True,
                                    on_delete=models.CASCADE)
    referent = models.BooleanField(default=False)

    def __str__(self):
        if not self.benevole.user.last_name and not self.benevole.user.first_name :
            return "{0}".format(self.benevole.user.username)
        else:
            return "{0} {1}".format(self.benevole.user.last_name.upper(), \
                                    self.benevole.user.first_name.capitalize())


# paramètres specifiques organisateur de l'evenement
class ProfileOrganisateur(models.Model):
    UUID_Organisateur = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    # supprime l'organisateur si l'entree benevole est supprimee
    benevole = models.OneToOneField(ProfileBenevole,
                                    default='',
                                    null=True,
                                    on_delete=models.CASCADE)

    def __str__(self):
        if not self.benevole.user.last_name and not self.benevole.user.first_name :
            return "{0}".format(self.benevole.user.username)
        else:
            return "{0} {1}".format(self.benevole.user.last_name.upper(), \
                                    self.benevole.user.first_name.capitalize())

# paramètres specifiques responsable d'equipe
class ProfileResponsable(models.Model):
    UUID_Responsable = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    # supprime le responsable si l'entree benevole est supprimee
    benevole = models.OneToOneField(ProfileBenevole,
                                    default='',
                                    null=True,
                                    on_delete=models.CASCADE)

    def __str__(self):
        if not self.benevole.user.last_name and not self.benevole.user.first_name :
            return "{0}".format(self.benevole.user.username)
        else:
            return "{0} {1}".format(self.benevole.user.last_name.upper(), \
                                    self.benevole.user.first_name.capitalize())

'''

# hook create_or_update_user_profile methode.
# quand on crée un user sur le projet, ce hook vient aussi lui creer une entree dans la table benevole
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        ProfileBenevole.objects.create(user=instance)
    # instance.profile.save()
'''

# crée nos groupe à la fin de la migration, grace au hook
@receiver(post_migrate)
def init_groups(sender, **kwargs):
    gest = 'GESTIONNAIRE'
    orga = 'ORGANISATEUR'
    bene = 'BENEVOLE'

    groupe_liste = [
        (gest, 'Gestionnaire'),
        (orga, 'Organisateur'),
        (bene, 'Bénévole'),
    ]
    for code_quadri, nom in groupe_liste:
        group, created = Group.objects.get_or_create(name=nom)
        if created:
            # group.permissions.add(can_edit_user)
            logger.info('{0} Group created'.format(nom))
        group, created = Group.objects.get_or_create(name=nom)
