from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User, Group

from administration.models import groupe_liste
from benevole.models import ProfileGestionnaire, ProfilePersonne, ProfileOrganisateur, ProfileResponsable, \
    ProfileBenevole


#    quand on crée un user sur le projet, ce hook vient aussi lui creer une entree dans la table profilePersonne
#    sender: sender model from which you'll receive signal from
#    instance: model instance(record) which is saved
#    hook save ou update du User model.

#@receiver(post_save, sender=User)
#def create_or_update_user_profile(sender, instance, created, **kwargs):
#    if created:     # creation
#        ProfilePersonne.objects.create(user=instance)
#    else:           # update
#        instance.profile.save()

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, **kwargs):
    print ('User changed hooked')
    if kwargs.get('created', True):     # creation
        ProfilePersonne.objects.create(user=instance)
    else:           # update
        instance.profile.save()

############################
#  gestion des groupes auto
#  marche pas bien a voir
#  creer les delete et rassembler dans une seule def avec tous les decorateurs dessus
############################

#   quand on vient creer une entrée dans le profile *** on affecte le groupe *** au User
@receiver(post_save, sender=ProfileGestionnaire)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    print("on recupere le signal de ProfileGestionnaire ")
    if created:
        # groupe_liste[0][1] : definit le groupe gestionnaire dans administration.model
        the_group = Group.objects.get(name=groupe_liste[0][1])
        profpers = ProfilePersonne.objects.get(UUID_personne=instance.personne_id)
        the_user = User.objects.get(id=profpers.user_id)
        the_group.user_set.add(the_user)


#   quand on vient creer une entrée dans le profile *** on affecte le groupe *** au User
@receiver(post_save, sender=ProfileOrganisateur)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    print("on recupere le signal de ProfileOrganisateur ")
    if created:
        # groupe_liste[1][1] : definit le groupe organisateur dans administration.model
        the_group = Group.objects.get(name=groupe_liste[1][1])
        profpers = ProfilePersonne.objects.get(UUID_personne=instance.personne_id)
        the_user = User.objects.get(id=profpers.user_id)
        the_group.user_set.add(the_user)


#   quand on vient creer une entrée dans le profile *** on affecte le groupe *** au User
@receiver(post_save, sender=ProfileResponsable)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    print("on recupere le signal de ProfileResponsable ")
    if created:
        # groupe_liste[2][1] : definit le groupe responsable dans administration.model
        the_group = Group.objects.get(name=groupe_liste[2][1])
        profpers = ProfilePersonne.objects.get(UUID_personne=instance.personne_id)
        the_user = User.objects.get(id=profpers.user_id)
        the_group.user_set.add(the_user)


#   quand on vient creer une entrée dans le profile *** on affecte le groupe *** au User
@receiver(post_save, sender=ProfileBenevole)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    print("on recupere le signal de ProfileBenevole ")
    if created:
        # groupe_liste[3][1] : definit le groupe benevole dans administration.model
        the_group = Group.objects.get(name=groupe_liste[3][1])
        profpers = ProfilePersonne.objects.get(UUID_personne=instance.personne_id)
        the_user = User.objects.get(id=profpers.user_id)
        the_group.user_set.add(the_user)
