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
    nom = models.CharField(max_length=50,
                           verbose_name="association repésentée par le bénévole")

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
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE) # supprime cette personne si le user est supprimé
    UUID_personne = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    # on ne peut pas supprimer une asso origine tant
    # qu'une personne en fait partie
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
    # supprime le gestionnaire si l'entree personne est supprimee
    personne = models.OneToOneField(ProfilePersonne,
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
        if not self.personne.user.last_name and not self.personne.user.first_name :
            return "{0}".format(self.personne.user.username)
        else:
            return "{0} {1}".format(self.personne.user.last_name.upper(), \
                                    self.personne.user.first_name.capitalize())


# paramètres specifiques organisateur de l'evenement
class ProfileOrganisateur(models.Model):
    UUID_organisateur = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    # supprime l'organisateur si l'entree personne est supprimee
    personne = models.OneToOneField(ProfilePersonne,
                                    default='',
                                    null=True,
                                    on_delete=models.CASCADE)
    # pas de sens
    # evenement = models.ForeignKey('evenement.Evenement',
    #                              default='',
    #                              null=True,
    #                              on_delete=models.CASCADE)

    def __str__(self):
        if not self.personne.user.last_name and not self.personne.user.first_name :
            return "{0}".format(self.personne.user.username)
        else:
            return "{0} {1}".format(self.personne.user.last_name.upper(), \
                                    self.personne.user.first_name.capitalize())

# paramètres specifiques responsable d'equipe
class ProfileResponsable(models.Model):
    UUID_responsable = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    # supprime le responsable si l'entree personne est supprimee
    personne = models.OneToOneField(ProfilePersonne,
                                    default='',
                                    null=True,
                                    on_delete=models.CASCADE)
    # pas de sens
    # equipe = models.ForeignKey('evenement.Equipe',
    #                           default='',
    #                           null=True,
    #                           on_delete=models.CASCADE)

    def __str__(self):
        if not self.personne.user.last_name and not self.personne.user.first_name :
            return "{0}".format(self.personne.user.username)
        else:
            return "{0} {1}".format(self.personne.user.last_name.upper(), \
                                    self.personne.user.first_name.capitalize())


# paramètres specifiques benevole
class ProfileBenevole(models.Model):
    UUID_benevole = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    # supprime le benevole si l'entree personne est supprimee
    personne = models.OneToOneField(ProfilePersonne,
                                    default='',
                                    null=True,
                                    on_delete=models.CASCADE)
    message = models.CharField(max_length=1000, blank=True, default='')

    def __str__(self):
        if not self.personne.user.last_name and not self.personne.user.first_name :
            return "{0}".format(self.personne.user.username)
        else:
            return "{0} {1}".format(self.personne.user.last_name.upper(), \
                                    self.personne.user.first_name.capitalize())


'''
# hook create_or_update_user_profile methode.
# quand on crée un user sur le projet, ce hook vient aussi lui creer une entree dans la table personne
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        ProfilePersonne.objects.create(user=instance)
    # instance.profile.save()
'''

# crée nos groupe à la fin de la migration, grace au hook
@receiver(post_migrate)
def init_groups(sender, **kwargs):
    gest = 'GESTIONNAIRE'
    orga = 'ORGANISATEUR'
    resp = 'RESPONSABLE'
    bene = 'BENEVOLE'

    groupe_liste = [
        (gest, 'Gestionnaire'),
        (orga, 'Organisateur'),
        (resp, 'Responsable'),
        (bene, 'Bénévole'),
    ]
    for code_quadri, nom in groupe_liste:
        group, created = Group.objects.get_or_create(name=nom)
        if created:
            # group.permissions.add(can_edit_user)
            logger.info('{0} Group created'.format(nom))
        group, created = Group.objects.get_or_create(name=nom)
