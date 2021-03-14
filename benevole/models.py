import uuid

from django.db.backends.utils import logger
from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    UUID_personne = \
        models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    UUID_origine = \
        models.ForeignKey(Origine, primary_key=False, null=True, blank=True, default='', on_delete=models.DO_NOTHING)
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


# hook create_or_update_user_profile methode.
# quand on crée un user sur le projet, ce hook vient aussi lui creer une entree dans la table benevole
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        ProfileBenevole.objects.create(user=instance)
    # instance.profile.save()


# crée nos groupe à la fin de la migration, grace au hook
@receiver(post_migrate)
def init_groups(sender, **kwargs):
    #permission and group code goes here
    group, created = Group.objects.get_or_create(name='Gestionnaire')
    if created:
        #group.permissions.add(can_read_campaign)
        logger.info('Gestionnaire Group created')
    group, created = Group.objects.get_or_create(name='Organisateur')
    if created:
        logger.info('Organisateur Group created')
    group, created = Group.objects.get_or_create(name='Bénévole')
    if created:
        logger.info('Bénévole Group created')
    group, created = Group.objects.get_or_create(name='plop')
    if created:
        logger.info('plop Group created')
