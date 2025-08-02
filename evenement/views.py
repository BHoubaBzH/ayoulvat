from django.db import connection
from administration.views import inscription_ouvert
from datetime import datetime,timedelta, date

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q

from utils.generic import *
from utils.evenement import *
from utils.benevole import *
from utils.administration import *
from ayoulvat.languages import *

from evenement.forms import EquipeForm, PlanningForm, PosteForm, CreneauForm
from evenement.models import Evenement, Equipe, Planning, Poste, Creneau
from benevole.models import ProfileBenevole
#from benevole.views import ListeGroupesUserFiltree, check_majeur, devenir_benevole
from association.models import Association, AssoPartenaire

from django.http import HttpResponse
from django.contrib import messages

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

################################################
#            view liste_evenements
################################################
@login_required(login_url='login')
def liste_evenements(request):
    """
    liste les evenements de l'asso
    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    logger.info(f'\n################## {__name__} #####################\n')
    if request.method == 'GET' and 'uuid_asso' in request.GET :
        logger.info('get')
        # récupère dans url uuid de l association
        uuid_asso = request.GET.get('uuid_asso')
    else:
         # récupère dans la session uuid de l association
        uuid_asso = request.session['uuid_association']
    association = Association.objects.get(UUID=uuid_asso)

    try: # on filtre les évènements sur ceux de l asso uniquement
        liste_evenements = Evenement.objects.filter(association_id=uuid_asso).order_by("debut")
    except:
        logger.info('Pas encore d\'évènement pour cette asso, voulez-vous en creer un?')

    data = {
        "Association": association,
        "Evenements": liste_evenements,
        "Text": text_template[language], # textes traduits 
    }

    # check des roles du user sur :
    logger.info('#########################################################')
    logger.info('#   utilisateur connecté: ')
    logger.info(f'#        {request.user.first_name} {request.user.last_name} ')
    logger.info('#   roles : ')
    # groupes/roles de l utilisateur sur l asso
    #try:
    RolesUtilisateur = ListeGroupesUserFiltree(request, "ass", association)
    for role in RolesUtilisateur:
        data[role] = "oui" # passe les roles 
    #except:
    #    logger.error('erreur dans les RolesUtilisateur')
    logger.info('#########################################################')    

    return render(request, "evenement/partials/base_evenement.html", data)

################################################
#            view evenement
################################################

@login_required(login_url='login')
def evenement(request, uuid_evenement):
    """
        page d'un evenement
    """
    logger.info(f'\n################## {__name__} #####################\n')

    logger.info(f'*** Debut traitement view : {datetime.now()}')
    # store dans la session le uuid de l'evenement
    # il apparait dans l'url pour pouvoir donner le liens directe aux bénévoles par la suite
    request.session['uuid_evenement'] = uuid_evenement.urn

    # on construit nos objets a passer au template dans le dictionnaire data
    evenement = Evenement.objects.get(UUID=uuid_evenement)
    # récupère dans la session l'uuid de l'association, si on est passé par l'asso
    uuid_asso= evenement.association_id
    # on stock dans la session
    request.session['uuid_association'] = uuid_asso.urn
    data = {
        "Association": evenement.association,
        "Evenement": evenement,
        "Equipes":  list(evenement.equipe_set.order_by('nom').select_related('evenement')),  # objets equipes de l'evenement
        "Plannings": list(evenement.planning_set.order_by('debut').select_related('equipe', 'evenement')),  # objets planning de l'evenement

        "dispo_actif": "False", # active ou non la gestion des disponibilités par les bénévoles; par défaut désactivé

        "Planning": "",  # objet planning selectionné
        "Creneaux_plage": "",  # objets creneaux de l'evenement entre 2 dateheure
        "equipe_uuid": "",  # par defaut, pas d'equipe selectionée
        "planning_uuid": "",  # par defaut, pas de planning selectionée
        "PlanningRange": "",  # dictionnaire formaté des dates heures de l'objet selectionné
        "equipes_avec_planning": list(evenement.equipe_set.filter(planning__isnull=False).order_by('nom').distinct().select_related('evenement')), # liste des équipes avec au moins un planning
        "creneaux_benevole" : list(evenement.creneau_set.filter(benevole_id=request.user.profilebenevole.UUID).order_by('debut').select_related('poste', 'planning', 'equipe', 'benevole', 'evenement')), # crenaux du bénévole connecté
        
        "FormEquipe" : EquipeForm(initial={'evenement': evenement}), # form non liée au template pour ajout d une nouvelle equipe
        "FormPlanning" : "", # form non liée au template pour ajout d un nouveau planning
        "DicPostes" : "",  # dictionnaire des formes de poste de l'evenement liées aux objets de la db
        "FormPoste" : "",  # form non liée au template pour ajout d un nouveau poste
        "DicCreneaux" : "",  # dictionnaire des formes de creneau de l'evenement liées aux objets de la db
        "FormCreneau" : "",  # form non liée au template pour ajout d un nouveau creneau
        "Majeur" : check_majeur(request.user.date_de_naissance, evenement.debut.date()), # booleen précisant si le bénévole est majeur
        "EvtOuvertBenevoles" : inscription_ouvert(evenement.inscription_debut, evenement.inscription_fin) , # integer précisant si on est avant/dans/après la période de modification des creneaux
        "Text": text_template[language], # textes traduits 
    }

    data["FormPlanning"] = PlanningForm(initial={'evenement': evenement, 'equipe': data["equipe_uuid"]})
    data["PlanningCreneauxDispo"] = PlanningCreneauxDispo(data["Plannings"]) # dic UUID planning , nb creneaux dispo 
    data["EvenementCreneauxDispo"] = Creneau.objects.filter(Q(evenement_id=evenement.UUID), Q(benevole_id__isnull=True)).count() # nb creneaux dispo sur l evenement

    # liste les roles de l'utilisateur et les envoi au template
    RolesUtilisateur = liste_roles_utilisateur(request, evenement)
    for role, value in RolesUtilisateur.items():
        if value: data[role] = value 

    try:
        # partie servant a forcer le choix d une asso partenaire
        lien_ben_ev_assopart = evenement_benevole_assopart.objects.get(Q(evenement=evenement),Q(profilebenevole=request.user.profilebenevole))
        # le benevole a selectionne une asso, on sauvegarde
        if request.method == "POST" and 'asso_part_selected' in request.POST:
            lien_ben_ev_assopart.asso_part = AssoPartenaire.objects.get(UUID=request.POST.get('asso_part_selected'))
            lien_ben_ev_assopart.save()
        # logger.info(f' assos liées : {lien_ben_ev_assopart}')
        # check si une asso partenaire selectionnee par le benevole
        if lien_ben_ev_assopart.asso_part:
            # le benevole a une asso partenaire, on l envoie au template
            data["AssoPartUser"] = lien_ben_ev_assopart.asso_part
        else:
            # le benevole n a pas d asso partenaire, envoie vide au template pour forcer le choix si besoins
            data["AssoPartUser"] = ""
    except:
        # admin, non bénévole, voulant voir la vue bénévole
        pass

    # recupere les POST, but est de tout gerer dans une seule page
    # et d'afficher les infos en fonction des POST recus :
    if request.method == "POST":

        # log les donnees post
        log_post(request.POST)

        # le bénévole prend ou libère un créneau
        # traitement normal, ne force pas le retour sur le planning global de l evenement
        if any(x in  request.POST for x in ['benevole_prend_creneau', 'benevole_libere_creneau']):
            creneau_bene = Creneau.objects.get(UUID=request.POST.get('creneau'))
            creneau_bene.benevole_id = request.user.profilebenevole.UUID if ('benevole_prend_creneau' in request.POST) else ""
            creneau_bene.save()
            # messages aux bénévoles
            if ('benevole_prend_creneau' in request.POST):
                #messages.success(request, inscr_creneau_success)
                messages.success(request, flash[language]['inscr_creneau_success'])
            if ('benevole_libere_creneau' in request.POST):
                messages.info(request, flash[language]['free_creneau_success'])

        # dans equipe
        if request.POST.get('equipe'):  
            # selection d'une équipe

            # UUID equipe selectionnée
            data["equipe_uuid"] = request.POST.get('equipe')  
            data["planning_uuid"] = request.POST.get('planning')
            data["Planning"] = Planning.objects.get(UUID=data["planning_uuid"])  # planning selectionnée
            # instances de form poste & creneau liées : modifs & suppression & liste des postes
            data["PlanningRange"] = planning_range(data["Planning"].debut,
                                                data["Planning"].fin,
                                                data["Planning"].pas)
            # retourne les creneaux d'un evenement sur une plage et sur tous les plannings 
            # permet de savoir si le user est occupe sur la plage 
            data["Creneaux_plage"] = \
                tous_creneaux_entre_2_heures(data["Planning"].debut,
                                                data["Planning"].fin,
                                                evenement)

            # envoi les forms au template
            if data["planning_uuid"]:
                planning = Planning.objects.get(UUID=data["planning_uuid"])
                data["DicPostes"] = dic_forms_postes(planning)
                data["DicCreneaux"] = dic_forms_creneaux(request, planning, RolesUtilisateur)
                data["PostesCreneaux"] = postes_creneaux(planning)

        else:  
            # selection d'un evenement uniquement
            # pas de 30 minutes par défaut a voir pour variabiliser
            data["PlanningRange"] = planning_range(evenement.debut, evenement.fin, 30)
            # si la personne a cliqué sur le bouton pour recevoir ses créneaux par email
            if 'creneaux_courriel' in request.POST:
                try:
                    envoi_courriel_plan_perso(request, evenement)
                    messages.success(request, flash[language]['message_sent_success'])
                except:
                    messages.error(request, flash[language]['message_sent_error'])
            # un admin/orga veut devenir bénévole sur l evenement
            if 'devenir_benevole' in request.POST:
                devenir_benevole(request.user, EVENEMENT=evenement)
        
        # si le benevole appuie sur le bouton "mon planning"
        if request.POST.get('planning_perso'):
            data["planning_perso"] = "oui"
            data["PlanningRange"] = planning_range(evenement.debut,
                                                evenement.fin,
                                                30)
        if request.POST.get('planning_global'):
            data["planning_global"] = "oui"


        # recupere l info si le lien vers une page admin ou autre
        # important pour garder l'affichage de la grid avec les boutons entre autre
        data["PageType"] = request.POST.get('PageType') 

        # recalcule la liste des plannings avant le render
        data["Plannings"] = evenement.planning_set.order_by('debut').select_related('equipe', 'evenement')

    # pas de données post, on arrive de la page des evenements, affiche le planning global de l'evenement
    else:
        data["PlanningRange"] = planning_range(evenement.debut,
                                            evenement.fin,
                                            30)
    # le planning commence avant 17h, on affiche le nom de la priere journee en entete de grid
    planningStartHour = data["PlanningRange"][list(data["PlanningRange"].keys())[0]][0][:2]
    if ( int(planningStartHour) <= 17 ):
        logger.info(f' on cemmence avant midi')
        data["DisplayFirstDayName"] = 'True'

    logger.info(f'*** Fin traitement view : {datetime.now()}')
    return render(request, "evenement/partials/base_evenement.html", data)
