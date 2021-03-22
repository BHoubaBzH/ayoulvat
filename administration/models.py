import uuid

from django.db.backends.utils import logger
from django.contrib.auth.models import Group, Permission
from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver


class Formule(models.Model):
    UUID_formule = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    nom = models.CharField(max_length=100)
    cout = models.IntegerField(default=0)
    description = models.CharField(max_length=500, blank=True, default='')

    def __str__(self):
        return self.nom


class Logs(models.Model):
    jour = models.DateField()
    heure = models.TimeField()
    log = models.CharField(max_length=250)

    def __str__(self):
        return self.log

# crée nos groupe à la fin de la migration, grace au hook
# on crée également les droits affectés aux groupes
@receiver(post_migrate)
def init_groups(sender, **kwargs):
    gest = 'GESTIONNAIRE'   # gestionnaire d'asso
    orga = 'ORGANISATEUR'   # organisateur d'evenement
    resp = 'RESPONSABLE'    # responsable d'equipe
    bene = 'BENEVOLE'       # bénévole affecté aux creneaux

    groupe_liste = [
        (gest, 'Gestionnaire'),
        (orga, 'Organisateur'),
        (resp, 'Responsable'),
        (bene, 'Benevole'),
    ]

    groupe_permission = {
        'Gestionnaire': (  # asso
                         'add_abonnement', 'view_abonnement',
                         'add_association', 'view_association', 'change_association', 'delete_association',
                           # users
                         'add_user', 'view_user', 'change_user', 'delete_user',
                         'add_profilegestionnaire', 'view_profilegestionnaire', 'change_profilegestionnaire',
                         'delete_profilegestionnaire',
                         'add_profileorganisateur', 'view_profileorganisateur', 'change_profileorganisateur',
                         'delete_profileorganisateur',
                         'add_profileresponsable', 'view_profileresponsable', 'change_profileresponsable',
                         'delete_profileresponsable',
                         'add_profilebenevole', 'view_profilebenevole', 'change_profilebenevole',
                         'delete_profilebenevole',
                         'add_profilepersonne', 'view_profilepersonne', 'change_profilepersonne',
                         'delete_profilepersonne',
                         'add_origine', 'view_origine', 'change_origine', 'delete_origine',
                           # evenement
                         'add_evenement', 'view_evenement', 'change_evenement', 'delete_evenement',
                         'add_equipe', 'view_equipe', 'change_equipe', 'delete_equipe',
                         'add_planning', 'view_planning', 'change_planning', 'delete_planning',
                         'add_poste', 'view_poste', 'change_poste', 'delete_poste',
                         'add_creneau', 'view_creneau', 'change_creneau', 'delete_creneau',
        ),
        'Organisateur': (  # users
                         'add_user', 'view_user', 'change_user', 'delete_user',
                         'view_profilegestionnaire',
                         'add_profileorganisateur', 'view_profileorganisateur', 'change_profileorganisateur',
                         'delete_profileorganisateur',
                         'add_profileresponsable', 'view_profileresponsable', 'change_profileresponsable',
                         'delete_profileresponsable',
                         'add_profilebenevole', 'view_profilebenevole', 'change_profilebenevole',
                         'delete_profilebenevole',
                         'add_profilepersonne', 'view_profilepersonne', 'change_profilepersonne',
                         'delete_profilepersonne',
                         'add_origine', 'view_origine', 'change_origine', 'delete_origine',
                           # evenement
                         'add_evenement', 'view_evenement', 'change_evenement', 'delete_evenement',
                         'add_equipe', 'view_equipe', 'change_equipe', 'delete_equipe',
                         'add_planning', 'view_planning', 'change_planning', 'delete_planning',
                         'add_poste', 'view_poste', 'change_poste', 'delete_poste',
                         'add_creneau', 'view_creneau', 'change_creneau', 'delete_creneau',
        ),
        'Responsable': (   # users
                         'add_user', 'view_user', 'change_user', 'delete_user',
                         'view_profilegestionnaire',
                         'view_profileorganisateur',
                         'add_profileresponsable', 'view_profileresponsable', 'change_profileresponsable',
                         'delete_profileresponsable',
                         'add_profilebenevole', 'view_profilebenevole', 'change_profilebenevole',
                         'delete_profilebenevole',
                         'add_profilepersonne', 'view_profilepersonne', 'change_profilepersonne',
                         'delete_profilepersonne',
                         'view_origine',
                           # evenement
                         'view_evenement',
                         'add_equipe', 'view_equipe', 'change_equipe', 'delete_equipe',
                         'add_planning', 'view_planning', 'change_planning', 'delete_planning',
                         'add_poste', 'view_poste', 'change_poste', 'delete_poste',
                         'add_creneau', 'view_creneau', 'change_creneau', 'delete_creneau',
        ),
        'Benevole': (      # users
                         'add_user', 'view_user', 'change_user', 'delete_user',
                         'view_profilegestionnaire',
                         'view_profileorganisateur',
                         'view_profileresponsable',
                         'add_profilebenevole', 'view_profilebenevole', 'change_profilebenevole',
                         'delete_profilebenevole',
                         'add_profilepersonne', 'view_profilepersonne', 'change_profilepersonne',
                         'delete_profilepersonne',
                         'view_origine',
                           # evenement
                         'view_evenement',
                         'add_equipe', 'view_equipe', 'change_equipe', 'delete_equipe',
                         'add_planning', 'view_planning', 'change_planning', 'delete_planning',
                         'add_poste', 'view_poste', 'change_poste', 'delete_poste',
                         'add_creneau', 'view_creneau', 'change_creneau', 'delete_creneau',

        ),
    }


    for code_quadri, nom in groupe_liste:
        # on cree les groupes
        group, created = Group.objects.get_or_create(name=nom)
        # on nettoye les permissions des groupes
        group.permissions.clear()
        # on met à jour les autorisations des groupes
        for perm in groupe_permission[nom]:
            permission = Permission.objects.get(codename=perm)
            group.permissions.add(permission)
        if created:
            logger.info('{0} Group created'.format(nom))