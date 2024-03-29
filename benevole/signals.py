from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import Group

from administration.models import groupe_liste
from benevole.models import ProfileAdministrateur, Personne, ProfileOrganisateur, ProfileResponsable, \
    ProfileBenevole

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

#    quand on crée un user sur le projet, ce hook vient aussi lui creer une entree dans la table Personne
#    sender: sender model from which you'll receive signal from
#    instance: model instance(record) which is saved
#    hook save ou update du User model.
########################################################
#  creation auto de ProfilePersonne auto sur creation du User
########################################################
'''
@receiver(post_save, sender=User)
def create_or_update_profile_personne(sender, instance, **kwargs):
    print('change or create on {0} hooked'.format(sender.__name__))
    if kwargs.get('created', True):  # creation
        Personne.objects.create(user=instance)
'''

########################################################
#  gestion des groupes auto : ajoute / supprime le groupe associés suivant
#  la creation ou la suppression de l'entree dans la table profile associée
########################################################
def check_group(send_name):
    '''
    ramene le groupe sur le quel on travail en fonction de la table (le type de personne) editée
    '''
    if (send_name == 'ProfileAdministrateur'):
        # groupe_liste[0][1] : definit le groupe administrateur dans administration.model
        temp_group = Group.objects.get(name=groupe_liste[0][1])
    if (send_name == 'ProfileOrganisateur'):
        # groupe_liste[1][1] : definit le groupe organisateur dans administration.model
        temp_group = Group.objects.get(name=groupe_liste[1][1])
    if (send_name == 'ProfileResponsable'):
        # groupe_liste[2][1] : definit le groupe responsable dans administration.model
        temp_group = Group.objects.get(name=groupe_liste[2][1])
    if (send_name == 'ProfileBenevole'):
        # groupe_liste[3][1] : definit le groupe benevole dans administration.model
        temp_group = Group.objects.get(name=groupe_liste[3][1])
        print('name : {}'.format(temp_group))
    return temp_group

@receiver(post_save, sender=ProfileAdministrateur)
@receiver(post_save, sender=ProfileOrganisateur)
@receiver(post_save, sender=ProfileResponsable)
@receiver(post_save, sender=ProfileBenevole)
def create_or_update_profiles(sender, instance, **kwargs):
    print('change or create on {0} hooked'.format(sender.__name__))
    if kwargs.get('created', True):  # creation
        the_group = check_group(sender.__name__)
        pers = Personne.objects.get(UUID=instance.personne_id)
        the_group.user_set.add(pers)

@receiver(post_delete, sender=ProfileAdministrateur)
@receiver(post_delete, sender=ProfileOrganisateur)
@receiver(post_delete, sender=ProfileResponsable)
@receiver(post_delete, sender=ProfileBenevole)
def delete_profiles(sender, instance, **kwargs):
    print('delete on {0} hooked'.format(sender.__name__))
    the_group = check_group(sender.__name__)
    try: 
        pers = Personne.objects.get(UUID=instance.personne_id)
        the_group.user_set.remove(pers)
    except:
        logger.info('suppression de la personne, déjà faite')
