import uuid

from django.db.backends.utils import logger
from django.contrib.auth.models import Group, Permission
from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver


##########################################################
# definition de nos groupes
##########################################################
admi = 'ADMINISTRATEUR'  # administrateur d'asso
orga = 'ORGANISATEUR'  # organisateur d'evenement
resp = 'RESPONSABLE'  # responsable d'equipe
bene = 'BENEVOLE'  # bénévole affecté aux creneaux

groupe_liste = [
    (admi, 'Administrateur'),
    (orga, 'Organisateur'),
    (resp, 'Responsable'),
    (bene, 'Benevole'),
]

"""
groupe_permission = {
    'Administrateur': (  # asso
        'add_abonnement', 'view_abonnement',
        'add_association', 'view_association', 'change_association', 'delete_association',
        # custom user : personne
        'add_personne', 'view_personne', 'change_personne', 'delete_personne',
        'add_profileadministrateur', 'view_profileadministrateur', 'change_profileadministrateur',
        'delete_profileadministrateur',
        'add_profileorganisateur', 'view_profileorganisateur', 'change_profileorganisateur',
        'delete_profileorganisateur',
        'add_profileresponsable', 'view_profileresponsable', 'change_profileresponsable',
        'delete_profileresponsable',
        'add_profilebenevole', 'view_profilebenevole', 'change_profilebenevole',
        'delete_profilebenevole',
        'add_assopartenaire', 'view_assopartenaire', 'change_assopartenaire', 'delete_assopartenaire',
        # evenement
        'add_evenement', 'view_evenement', 'change_evenement', 'delete_evenement',
        'add_equipe', 'view_equipe', 'change_equipe', 'delete_equipe',
        'add_planning', 'view_planning', 'change_planning', 'delete_planning',
        'add_poste', 'view_poste', 'change_poste', 'delete_poste',
        'add_creneau', 'view_creneau', 'change_creneau', 'delete_creneau',
    ),
    'Organisateur': (  # custom user : personne
        'add_personne', 'view_personne', 'change_personne', 'delete_personne',
        'view_profileadministrateur',
        'add_profileorganisateur', 'view_profileorganisateur', 'change_profileorganisateur',
        'delete_profileorganisateur',
        'add_profileresponsable', 'view_profileresponsable', 'change_profileresponsable',
        'delete_profileresponsable',
        'add_profilebenevole', 'view_profilebenevole', 'change_profilebenevole',
        'delete_profilebenevole',
        'add_assopartenaire', 'view_assopartenaire', 'change_assopartenaire', 'delete_assopartenaire',
        # evenement
        'add_evenement', 'view_evenement', 'change_evenement', 'delete_evenement',
        'add_equipe', 'view_equipe', 'change_equipe', 'delete_equipe',
        'add_planning', 'view_planning', 'change_planning', 'delete_planning',
        'add_poste', 'view_poste', 'change_poste', 'delete_poste',
        'add_creneau', 'view_creneau', 'change_creneau', 'delete_creneau',
    ),
    'Responsable': (  # custom user : personne . responsable d'équipe
        'add_personne', 'view_personne', 'change_personne', 'delete_personne',
        'view_profileadministrateur',
        'view_profileorganisateur',
        'add_profileresponsable', 'view_profileresponsable', 'change_profileresponsable',
        'delete_profileresponsable',
        'add_profilebenevole', 'view_profilebenevole', 'change_profilebenevole',
        'delete_profilebenevole',
        'view_assopartenaire',
        # evenement
        'view_evenement',
        'view_equipe', 'change_equipe', 'delete_equipe',
        'view_planning', 'change_planning', 'delete_planning',
        'add_poste', 'view_poste', 'change_poste', 'delete_poste',
        'add_creneau', 'view_creneau', 'change_creneau', 'delete_creneau',
    ),
    'Benevole': (  # custom user : personne
        'view_personne', 'change_personne',
        'view_profileadministrateur',
        'view_profileorganisateur',
        'view_profileresponsable',
        'view_profilebenevole',
        'view_assopartenaire',
        # evenement
        'view_evenement',
        'view_equipe',
        'view_planning',
        'view_poste',
        'view_creneau',
    ),
}
"""
##########################################################


class Formule(models.Model):
    UUID = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    nom = models.CharField(max_length=100)
    cout = models.IntegerField(default=0)
    description = models.CharField(max_length=500, blank=True, default='')

    def __str__(self):
        return self.nom


class Logs(models.Model):
    UUID = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    jour = models.DateField()
    heure = models.TimeField()
    log = models.CharField(max_length=500)

    def __str__(self):
        return self.log

# crée nos groupes à la fin de la migration, grace au hook
# on crée également les droits affectés aux groupes
@receiver(post_migrate)
def init_groups(sender, **kwargs):
    for code_quadri, nom in groupe_liste:
        # on cree les groupes
        Group.objects.get_or_create(name=nom)

        # on utilise plus les perms django donc on retire ceci

        # on nettoye les permissions des groupes
        #group.permissions.clear()
        # on met à jour les autorisations des groupes
        #for perm in groupe_permission[nom]:
        #    #print(' permission : {}'.format(perm))
        #    permission = Permission.objects.get(codename=perm)
        #    group.permissions.add(permission)
        #if created:
        #    logger.info('{0} Group created'.format(nom))