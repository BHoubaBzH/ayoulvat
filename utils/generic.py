"""
fichier de déclaration des fonctions génériques du projet
"""
from django.core.mail import BadHeaderError, send_mail
from django.http import HttpResponse, HttpResponseRedirect

from evenement.models import Evenement, Equipe, Planning, Poste, Creneau
from benevole.models import ProfileBenevole, ProfileResponsable, ProfileOrganisateur, ProfileAdministrateur

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

################################################
#             fonctions
################################################

def envoi_courriel(sujet, message_text, from_courriel, to_courriel, message_html):
    try:
        send_mail(sujet, message_text, from_courriel, to_courriel, html_message=message_html)
    except BadHeaderError:
        return HttpResponse('Header incorrect détecté.')
    return HttpResponseRedirect('')

def envoi_courriel_orga_inscription(request):
    """
        envoi un courrier quand un bénévole s inscrit a l evenement
    """
    evt_uuid = request.POST.get('inscription_event')
    evt = Evenement.objects.get(UUID=evt_uuid)
    emails_orga = []
    logger.debug(f'evt nom : {evt.nom}')
    logger.debug(f'ben nom : {request.user}')
    for orga in evt.organisateur.all():
        emails_orga.append(orga.personne.email)
    if emails_orga:
        sujet = '[Ayoulvat] Nouveau bénévole inscrit à ton évènement'
        message_text = '{} vient de s\'inscrit à l\'évènement {} comme bénévole'.format(request.user, evt)
        message_html = ' \
            <html> <head> </head> <body> {} vient de s\'inscrit à l\'évènement {} comme bénévole</body> </html> \
            '.format(request.user, evt)
        from_courriel = 'no-reply@deusta.bzh'
        to_courriel = emails_orga
        logger.debug(to_courriel)
        if sujet and to_courriel and from_courriel:
            envoi_courriel(sujet, message_text, from_courriel, to_courriel, message_html)

def RoleUtilisateur(request, objet="", filtre=""): # remplace GroupeUtilisateur pour avoir le role par evenement
    """
        renvoi les roles du user connecte 
        filtre si en parametre est passé 
        ass : pour l'asso uniquement
        ev : pour l'evenement uniquement
        eq : pour l'equipe uniquement
        plan : pour le planning uniquement

        sortie
            dictionnaire: groupe, queryset
    """
    association, evenement, equipe, planning = "", "" , "", ""
    logger.debug(f'objet : {objet}')
    # test !
    if objet=='plan':
        # roles de la personne dans le planning
        planning = filtre
        administrateur = f'ProfileAdministrateur.objects.get(personne=request.user).AdministrateurAssociation.filter(UUID=planning.evenement.association_id)'
        organisateur = f'ProfileOrganisateur.objects.get(personne=request.user).OrganisateurEvenement.filter(UUID=planning.evenement_id)'
        responsable = f'ProfileResponsable.objects.get(personne=request.user).ResponsableEquipe.filter(UUID=planning.equipe_id)'
        benevole = f'ProfileBenevole.objects.get(personne=request.user).BenevolesEvenement.filter(UUID=planning.evenement_id)' # benevole inscrit a l evenement
        #benevole = f'ProfileBenevole.objects.get(personne=request.user).BenevolesCreneau.filter(planning=planning)'
    if objet=='eq':
        # roles de la personne dans l equipe
        equipe = filtre
        administrateur = f'ProfileAdministrateur.objects.get(personne=request.user).AdministrateurAssociation.filter(UUID=equipe.evenement.association_id)'
        organisateur = f'ProfileOrganisateur.objects.get(personne=request.user).OrganisateurEvenement.filter(UUID=equipe.evenement_id)'
        responsable = f'ProfileResponsable.objects.get(personne=request.user).ResponsableEquipe.filter(UUID=equipe_id)'
        benevole = f'ProfileBenevole.objects.get(personne=request.user).BenevolesEvenement.filter(UUID=equipe.evenement_id)' # benevole inscrit a l evenement
        #benevole = f'ProfileBenevole.objects.get(personne=request.user).BenevolesCreneau.filter(equipe=equipe)'

    if objet=='ev':
        # roles de la personne dans l evenement
        evenement = filtre
        #print(f'{evenement.association_id}')
        administrateur = f'ProfileAdministrateur.objects.get(personne=request.user).AdministrateurAssociation.filter(UUID=evenement.association_id)'
        organisateur = f'ProfileOrganisateur.objects.get(personne=request.user).OrganisateurEvenement.filter(UUID=evenement.UUID)'
        responsable = f'ProfileResponsable.objects.get(personne=request.user).ResponsableEquipe.filter(evenement=evenement)'
        benevole = f'ProfileBenevole.objects.get(personne=request.user).BenevolesEvenement.filter(UUID=evenement.UUID)' # benevole inscrit a l evenement
        #benevole = f'ProfileBenevole.objects.get(personne=request.user).BenevolesCreneau.filter(evenement=evenement)'
    if objet=='ass':
        # roles de la personne dans l asso
        association = filtre
        administrateur = f'ProfileAdministrateur.objects.get(personne=request.user).AdministrateurAssociation.filter(UUID=association.UUID)'
        organisateur = f'ProfileOrganisateur.objects.get(personne=request.user).OrganisateurEvenement.filter(association=association)'
        responsable = f'ProfileResponsable.objects.get(personne=request.user).ResponsableEquipe.filter(evenement__association=association)'
        benevole = f'ProfileBenevole.objects.get(personne=request.user).BenevolesEvenement.filter(association=association)' # benevole inscrit a un des evenement de l asso
        #benevole = f'ProfileBenevole.objects.get(personne=request.user).BenevolesCreneau.filter(evenement__association=association)'
    if not planning and not equipe and not evenement and not association:
        # roles de la personne sur tout le logiciel
        administrateur = f'ProfileAdministrateur.objects.get(personne=request.user).AdministrateurAssociation.all()'
        organisateur = f'ProfileOrganisateur.objects.get(personne=request.user).OrganisateurEvenement.all()'
        responsable = f'ProfileResponsable.objects.get(personne=request.user).ResponsableEquipe.all()'
        benevole = f'ProfileBenevole.objects.get(personne=request.user).BenevolesEvenement.all()'  # benevole inscrit a un evenement
        #benevole = f'ProfileBenevole.objects.get(personne=request.user).BenevolesCreneau.all()'
    out={}
    try:
        out['Administrateur'] = eval(f'{administrateur}')
    except:
        out['Administrateur'] = "" # la personne n est pas administrateur de asso
    try:
        out['Organisateur'] = eval(f'{organisateur}')
    except:
        out['Organisateur'] = "" # la personne n est pas organisateur d evenement
    try:
        out['Responsable'] = eval(f'{responsable}')
    except:
        out['Responsable'] = "" # la personne n est pas responsable d equipe
    try:
        out['Benevole'] = eval(f'{benevole}')
    except:
        out['Benevole'] = "" # la personne n est pas benevole
    return out

def ListeGroupesUserFiltree(request, objet="", filtre=""):
    """
        roles du user connecte
        filtre si en parametre est passé 
        objet :
            ass : pour l'asso uniquement
            ev : pour l'evenement uniquement
            eq : pour l'equipe uniquement
            plan : pour le planning uniquement
        filtre : objet bdd 

        sortie
            liste: groupes aux quel le user appartient en fonction du filtre
    """
    roles = RoleUtilisateur(request, objet, filtre)
    for role, entite in roles.items():
        if entite:
            logger.info(f'#        {role:<15} ->')
            for obj in entite:
                logger.info(f'#                               {obj.nom:<25}')    
    return roles

def liste_roles_utilisateur(request, evenement):
    '''
        retourne la liste des roles de l'utilisateur par rapport à l objet consulté
    '''
    # check des roles de user sur l evenement:
    logger.info('#########################################################')
    logger.info('#   utilisateur connecté: ')
    logger.info(f'#        {request.user.first_name} {request.user.last_name} ')
    logger.info('#   roles : ')
    # groupes/roles de l utilisateur
    if not request.method == "POST" or (request.POST.get('evenement') and not request.POST.get('equipe') and not request.POST.get('planning'))or request.POST.get('planning') and request.POST.get('planning_supprimer'):
        # pas de POST ou page evenement ou le planning vient d 'etre supprimé 
        objet = "ev"
        filtre = evenement
    elif request.POST.get('equipe') and not request.POST.get('planning'):
        # equipe et pas de planning
        objet = "eq"
        filtre = Equipe.objects.get(UUID=request.POST.get('equipe'))
    elif request.POST.get('planning') and not request.POST.get('planning_supprimer'):
        # planning et pas supprimé
        objet = "plan"
        filtre = Planning.objects.get(UUID=request.POST.get('planning'))
    else:
        # le benevole arrive sur la page de l evenement
        objet = "ev"
        filtre = evenement
    RolesUtilisateur = ListeGroupesUserFiltree(request, objet, filtre)
    logger.info('#########################################################') 
    return RolesUtilisateur

def log_post(post_datas):
    logger.info('#########################################################')
    logger.info('#   données POST passées: ')
    for key, value in post_datas.items():
        logger.info(f'#        POST -> {key} : {value}')
    logger.info('#########################################################')
