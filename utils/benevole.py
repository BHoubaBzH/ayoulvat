from django.core.mail import BadHeaderError, send_mail
from django.http import HttpResponse, HttpResponseRedirect

from evenement.models import Evenement, Equipe, Planning, Poste, Creneau
from benevole.models import ProfileBenevole

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

################################################
#            fonctions 
################################################
 
def check_majeur(date_naissance, date_evenement):
    '''
        vérifie si le bénévole est majeur ou non au debut de l'evenement
        entree : date de naissance du bénévole , date de début de l'evenement
        sortie : booleen , True : Majeur , False : Mineur
    '''
    pivot = 6570 # age pivot : 18 ans = 6570 jours
    delta = date_evenement - date_naissance
    if delta.days < pivot:
        return False # mineur
    else:
        return True # majeur

def devenir_benevole(user, **kwargs):
    # on ajoute le bénévole à l evenement
    if 'POST' in kwargs:
        # un benevole s inscrit a l evenement sur la page des evenements
        post = kwargs.get('POST')
        insc_ev = Evenement.objects.get(UUID=post.get('inscription_event'))
    elif 'EVENEMENT' :
        # un admin/orga decide de devenir benevole sur l evenement
        evt = kwargs.get('EVENEMENT')
        insc_ev = evt
    insc_be = ProfileBenevole.objects.get(personne_id=user.UUID)
    if insc_ev:
        logger.info('bénévole {} inscrit à l\'evenement {}'.format(insc_be, insc_ev))
        insc_ev.benevole.add(insc_be)