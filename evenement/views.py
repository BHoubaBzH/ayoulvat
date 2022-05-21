from django.db import connection
from administration.views import inscription_ouvert
from datetime import datetime,timedelta, date

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from ayoulvat.methods import envoi_courriel
from ayoulvat.languages import *

from evenement.forms import EquipeForm, PlanningForm, PosteForm, CreneauForm
from evenement.models import Evenement, Equipe, Planning, Poste, Creneau
from benevole.models import ProfileBenevole
from benevole.views import ListeGroupesUserFiltree, check_majeur, devenir_benevole
from association.models import Association

from django.http import HttpResponse
from django.contrib import messages

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

################################################
#             fonctions
################################################

def envoi_courriel_plan_perso(request, evenement):
    """
        envoi le courrier de résumé des creneaux du bénévole
    """
    sujet = f'voici ta liste de créneau pour l\'évènement {evenement}'
    message_text = request.POST.get('creneaux_courriel_message_text')
    message_html = request.POST.get('creneaux_courriel_message_html')
    from_courriel = 'no-reply@deusta.bzh'
    to_courriel = [(request.user.email)]
    logger.info(f'envoi des crenaux perso à : {request.user.email} ')
    if sujet and to_courriel and from_courriel:
        envoi_courriel(sujet, message_text, from_courriel, to_courriel, message_html)

def planning_range(debut, fin, delta):
    """
        entree : datetime, datetime, minutes
        retour : dictionnaire des dates (cles) et en valeurs listes heures , datetime par pas de delta minutes
        dates pour les style unique et bien placer le creneau dans le ccs grid
        heures pour l'affichage
        retour dict incrementé par delta:
        clés  : valeurs
        dates : ( heures, datetimes)
    """
    # logger.info('*** Debut fonction planning_range : {}'.format(datetime.now()))
    # logger.info('###### planning : {0} - {1}'.format(debut, fin))
    dates_heures = {}
    while debut <= fin:
        # logger.info('date : {}'.format(debut))
        date = debut.strftime("%Y-%m-%d-%H%M")
        heure = debut.strftime("%H:%M")
        dates_heures[date] = [heure, debut]
        debut += timedelta(minutes=delta)
    # logger.info('*** Fin fonction planning_range : {}'.format(datetime.now()))
    return dates_heures


def planning_retourne_pas(request):
    """
        entree:
            POST request
        sortie:
            pas_value : pas d'incrément du planning
        recuperer le pas du planning principalement pour les creneau et le choix des heures
    """
    if 'planning' in request.POST and not 'planning_supprimer'in request.POST :
        # retrouve le pas du planning à partir des infos du creneau
        Plan = Planning.objects.get(UUID=request.POST.get('planning'))
        pas_value = Plan.pas
    else:
        # pas possible normalement, on prévoit quand meme une valeur par défaut d une heure au pas
        pas_value = 60
    return pas_value


def tous_creneaux_entre_2_heures(debut, fin, uuid_evenement):
    """
        entree:
            date de début et de fin
            uuid de evenement
        sortie:
            creneaux : liste de creneaux
        donne tous les créneaux d'un evenement entre 2 date pour savor si un benevole est deja occupé
    """
    # logger.info('*** Debut fonction tous_creneaux_entre_2_heures : {}'.format(datetime.now()))
    crenos_out = []  # liste
    crenos = Creneau.objects.filter(evenement_id=uuid_evenement) 
    for creno in crenos:
        if debut <= creno.debut < fin and debut < creno.fin <= fin:
            crenos_out.append(creno)
        if creno.debut < debut < creno.fin <= fin:
            creno.debut = debut
            crenos_out.append(creno)
        if debut <= creno.debut < fin < creno.fin:
            creno.fin = fin
            crenos_out.append(creno)
        if creno.debut < debut and fin < creno.fin:
            creno.debut = debut
            creno.fin = fin
            crenos_out.append(creno)
        # logger.info(' creno : {}'.format(creno.nom))
    # logger.info('*** Fin fonction tous_creneaux_entre_2_heures : {}'.format(datetime.now()))
    return crenos_out

def postes_creneaux(evenementouplanning):
    """
        entrée : evenement ou planning
        sortie : dictionnaire clés : postes , valeurs : query set des creneaux du poste
    """
    postescreneaux={}
    postes=evenementouplanning.poste_set.order_by('nom')
    for poste in postes:
        #logger.info(f'POSTE : {poste}')
        creneaux= evenementouplanning.creneau_set.order_by('debut').filter(poste=poste).select_related('poste')
        #logger.info(f'CRENEAUX : {creneaux}')
        postescreneaux[poste]=creneaux
    return postescreneaux

def forms_equipe(request):
    """
        entree:
            la requete (contenant les infos POST)
        sortie:
            None
        gère la création, modification et suppression des equipes en fonction du contenu de POST
    """
    # logger.info('*** Debut fonction forms_equipe : {}'.format(datetime.now()))
    if any(x in request.POST for x in ['equipe_modifier', 'equipe_ajouter']):
        if 'equipe_modifier' in request.POST:
            formequipe = EquipeForm(request.POST,
                                  instance=Equipe.objects.get(UUID=request.POST.get('equipe')))
        # nouvel objet en base
        if 'equipe_ajouter' in request.POST:
            formequipe = EquipeForm(request.POST)
            logger.info(formequipe.errors)
        if formequipe.is_valid():
            logger.info('equipe modifié ou ajouté')
            formequipe.save()

    if request.POST.get('equipe_supprimer'):
        Equipe.objects.filter(UUID=request.POST.get('equipe_supprimer')).delete()
    return formequipe

def dic_forms_equipes(uuid_evenement):
    """
        entree:
            l'uid de l'evenement
        sortie:
            dictionnaire des forms équipe: key: UUID / val: form
    """
    # cree dans la page toutes nos from pour les equipes
    dic_equipe_init = {}  # dictionnaire des forms
    equipes = Equipe.objects.filter(evenement_id=uuid_evenement)
    for equipe in equipes:
        # form en lien avec l objet basé sur model et pk UUID equipe
        #formequipe = EquipeForm(instance=Equipe.objects.get(UUID=equipe.UUID)) # trop de queries db
        formequipe = EquipeForm(instance=equipe)
        dic_equipe_init[equipe.UUID] = formequipe  # dictionnaire des forms
        # logger.info(' equipe UUID : {}'.format(equipe.UUID))
    # logger.info('*** Fin fonction forms_equipe : {}'.format(datetime.now()))
    return dic_equipe_init

def forms_planning(request):
    """
        entree:
            la requete (contenant les infos POST)
        sortie:
            None
    """
    # logger.info('*** Debut fonction forms_planning : {}'.format(datetime.now()))
    formplanning = ""
    if any(x in request.POST for x in ['planning_modifier', 'planning_ajouter']):
        if 'planning_modifier' in request.POST:
            formplanning = PlanningForm(request.POST,
                                        instance=Planning.objects.get(UUID=request.POST.get('planning')),)
            if formplanning.is_valid():
                messages.success(request, flash[language]['plan_mod_success'])
                formplanning.save()
            else:
                messages.error(request, flash[language]['plan_mod_error'])
        # nouvel objet en base
        if 'planning_ajouter' in request.POST:
            formplanning = PlanningForm(request.POST)
            if formplanning.is_valid():
                messages.success(request, flash[language]['plan_new_success'])
                logger.info('planning modifié ou ajouté')
                formplanning.save()
            else:
                messages.error(request, flash[language]['plan_new_error'])
            

    if request.POST.get('planning_supprimer'):
        plan_supp = Planning.objects.get(UUID=request.POST.get('planning_supprimer'))
        logger.warn(f'planning supprimer : {plan_supp}')
        if not plan_supp.creneau_set.all():
            plan_supp.delete()
            messages.success(request, flash[language]['plan_sup_success'])
        else :
            messages.error(request, flash[language]['plan_sup_error'])
    return formplanning

def dic_forms_plannings(uuid_evenement):
    """
        entree:
            l'uid de l'evenement
        sortie:
            dictionnaire des forms planning: key: UUID / val: form
    """
    # cree dans la page toutes nos from pour les postes du planning
    dic_planning_init = {}  # dictionnaire des forms
    # key : UUID postes
    # val : form de poste initialisée objet db lié
    # parcours les plannings de l'evenement dans la base
    plannings = Planning.objects.filter(evenement_id=uuid_evenement)
    for planning in plannings:
        # form en lien avec l objet basé sur model et pk UUID equipe
        # formplanning = PlanningForm(instance=Planning.objects.get(UUID=planning.UUID)) # trop de queries db
        formplanning = PlanningForm(instance=planning)
        dic_planning_init[planning.UUID] = formplanning  # dictionnaire des forms
        # logger.info(' planning UUID : {}'.format(planning.UUID))
    # logger.info('*** Fin fonction forms_planning : {}'.format(datetime.now()))
    return dic_planning_init

def forms_poste(request):
    """
        entree:
            la requete (contenant les infos POST)
        sortie:
            None
        gère la création, modification et suppression de poste en fonction du contenu de POST
    """
    # logger.info('*** Debut fonction forms_postes : {}'.format(datetime.now()))
    # sauvegarde notre form modifée et crée envoyée en POST
    if any(x in request.POST for x in ['poste_modifier', 'poste_ajouter']):
        # form en lien avec l objet basé sur model et pk UUID poste
        if 'poste_modifier' in request.POST:
            formposte = PosteForm(request.POST,
                                  instance=Poste.objects.get(UUID=request.POST.get('poste')))
            if formposte.is_valid():
                formposte.save()
                messages.success(request, flash[language]['poste_mod_success'])
            else:
                messages.error(request, flash[language]['poste_mod_error'])
        # nouvel objet en base
        if 'poste_ajouter' in request.POST: 
            formposte = PosteForm(request.POST)
            if formposte.is_valid():
                formposte.save()
                messages.success(request, flash[language]['poste_new_success'])
            else:
                messages.error(request, flash[language]['poste_new_error'])
    # suppression du poste
    if request.POST.get('poste_supprimer'):
        poste_supp = Poste.objects.get(UUID=request.POST.get('poste_supprimer'))
        logger.warn(f'poste {poste_supp} supprimé')
        if not poste_supp.creneau_set.all():
            poste_supp.delete()
            messages.success(request, flash[language]['poste_sup_success'])
        else:
            messages.error(request, flash[language]['poste_sup_error'])
    return None

def dic_forms_postes(planning):
    """
        entree:
            uuid du planning en cours
        sortie:
            dictionnaire des forms postes: key: UUID / val: form
    """
    # cree dans la page toutes nos from pour les postes du planning
    dic_postes_init = {}  # dictionnaire des forms
    # parcours les postes du planning dans la base
    postes = planning.poste_set.all()
    for poste in postes:
        # form en lien avec l objet basé sur model et pk UUID poste
        #formposte = PosteForm(instance=Poste.objects.get(UUID=poste.UUID))  # trop de queries db
        formposte = PosteForm(instance=poste)
        dic_postes_init[poste.UUID] = formposte  # dictionnaire des forms
        #logger.info(' poste UUID : {1} form : {0}'.format(formposte, poste.UUID))
    return dic_postes_init

def forms_creneau(request):
    """
        entree:
            la requete (contenant les infos POST)
        sortie:
            Form
        gère la création, modification et suppression de creneaux en fonction du contenu de POST
    """
    pas = planning_retourne_pas(request)
    formcreneau = ""
    # logger.info('*** Debut fonction forms_creneaux : {}'.format(datetime.now()))
    if any(x in request.POST for x in ['creneau_modifier', 'creneau_ajouter']) and not request.POST.get('creneau_supprimer'):
        # form en lien avec l objet basé sur model et pk UUID creneau
        if 'creneau_modifier' in request.POST:
            formcreneau = CreneauForm(request.POST,
                                      instance=Creneau.objects.get(UUID=request.POST.get('creneau')),
                                      pas_creneau=pas,
                                      evenement=request.POST.get('evenement'),
                                      planning_uuid=request.POST.get('planning'),
                                      poste_uuid=request.POST.get('poste'),
                                      benevole_uuid=request.POST.get('benevole'),
                                      personne_connectee=request.user,
                                      type=request.POST.get('type'), )
            if formcreneau.is_valid():
                messages.success(request, flash[language]['creneau_mod_success'])
                formcreneau.save()
            else:
                messages.error(request, flash[language]['creneau_mod_error'])
        # nouvel objet en base
        if 'creneau_ajouter' in request.POST:
            formcreneau = CreneauForm(request.POST,
                                      pas_creneau=pas,
                                      evenement=request.POST.get('evenement'),
                                      planning_uuid=request.POST.get('planning'),
                                      poste_uuid=request.POST.get('poste'),
                                      benevole_uuid=request.POST.get('benevole'),
                                      personne_connectee=request.user,
                                      type=request.POST.get('type'), )
            if formcreneau.is_valid():
                messages.success(request, flash[language]['creneau_new_success'])
                formcreneau.save()
            else:
                messages.error(request, flash[language]['creneau_new_error'])

    if 'creneau_supprimer' in request.POST:
        cren_supp = Creneau.objects.get(UUID=request.POST.get('creneau'))
        logger.warn(f'creneau {cren_supp} supprimé')
        try:
            cren_supp.delete()
            messages.success(request, flash[language]['creneau_sup_success'])
        except:
            messages.error(request, flash[language]['creneau_sup_error'])
    # retourne la form avec l erreur si il y a 
    return formcreneau


def dic_forms_creneaux(request, planning):
    """
        entree:
            la requete (contenant les infos POST)
            le planning en cours
        sortie:
            dictionnaire des forms creneaux du planning: key: UUID / val: form
    """
    # cree dans la page toutes nos from pour les creneaux de l' evenement
    dic_creneaux_init = {}  # dictionnaire des forms
    pas = planning_retourne_pas(request)
    # key : UUID postes
    # val : form de creneau initialisée objet db lié
    # parcours les creneaux du planning dans la base
    creneaux = planning.creneau_set.all()
    for creneau in creneaux:  # liste des creneaux du planning
        # form en lien avec l objet basé sur model et pk UUID creneau
        #formcreneau = CreneauForm(instance=Creneau.objects.get(UUID=creneau.UUID),  # trop de queries db
        formcreneau = CreneauForm(instance=creneau,
                                  pas_creneau=pas, 
                                  evenement=request.POST.get('evenement'),
                                  planning_uuid=request.POST.get('planning'),
                                  poste_uuid=request.POST.get('poste'),
                                  benevole_uuid=request.POST.get('benevole'),
                                  personne_connectee=request.user,
                                  type=creneau._meta.get_field('type').value_from_object(creneau), )
        dic_creneaux_init[creneau.UUID] = formcreneau  # dictionnaire des forms: key: UUID / val: form
        # logger.info(' creneau UUID : {1} form : {0}'.format(formcreneau, creneau.UUID))
    # logger.info('*** Fin fonction forms_creneaux : {}'.format(datetime.now()))
    return dic_creneaux_init


################################################
#            views 
################################################
@login_required(login_url='login')
def liste_evenements(request):
    """
    liste les evenements de l'asso
    """
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
    }

    # check des roles de user sur l asso:
    logger.info('#########################################################')
    logger.info('#   utilisateur connecté: ')
    logger.info(f'#        {request.user.first_name} {request.user.last_name} ')
    logger.info('#   roles : ')
    # groupes/roles de l utilisateur sur l asso
    try:
        RolesUtilisateur = ListeGroupesUserFiltree(request, "", evenement)
        for role in RolesUtilisateur:
            data[role] = "oui" # passe les roles 
    except:
        logger.error('erreur dans les RolesUtilisateur')
    logger.info('#########################################################')    

    return render(request, "evenement/base_evenement.html", data)


@login_required(login_url='login')
@permission_required('evenement.view_evenement', login_url='login')
def evenement(request, uuid_evenement):
    """
        page d'un evenement
    """
    logger.info('')
    logger.info('*******************************************************')
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
        "Equipes":  evenement.equipe_set.order_by('nom'),  # objets equipes de l'evenement
        "Plannings": evenement.planning_set.order_by('debut').select_related('equipe'),  # objets planning de l'evenement
        #"Postes": evenement.poste_set.order_by('nom').select_related('planning', 'equipe', 'evenement'),  # objets postes de l'evenement pour planning perso
        #"Creneaux" : evenement.creneau_set.order_by('debut').select_related('poste', 'planning', 'equipe', 'evenement'),
        #"PostesCreneaux" : postes_creneaux(evenement),
        #"Benevoles": ProfileBenevole.objects.filter(BenevolesEvenement=evenement),  # objets benevoles de l'evenement

        "dispo_actif": "False", # active ou non la gestion des disponibilités par les bénévoles; par défaut désactivé

        "Planning": "",  # objet planning selectionné
        "Creneaux_plage": "",  # objets creneaux de l'evenement entre 2 dateheure
        "equipe_uuid": "",  # par defaut, pas d'equipe selectionée
        "planning_uuid": "",  # par defaut, pas de planning selectionée
        "PlanningRange": "",  # dictionnaire formaté des dates heures de l'objet selectionné
        "equipes_avec_planning": evenement.equipe_set.filter(planning__isnull=False).order_by('nom').distinct(), # liste des équipes avec au moins un planning
        "creneaux_benevole" : evenement.creneau_set.filter(benevole_id=request.user.profilebenevole.UUID).order_by('debut').select_related('poste', 'planning', 'equipe', 'evenement'), # crenaux du bénévole connecté
        
        "FormEquipe" : EquipeForm(initial={'evenement': evenement}), # form non liée au template pour ajout d une nouvelle equipe
        "DicEquipes" : dic_forms_equipes(evenement),
        "FormPlanning" : "", # form non liée au template pour ajout d un nouveau planning
        "DicPlannings" : dic_forms_plannings(evenement),
        "DicPostes" : "",  # dictionnaire des formes de poste de l'evenement liées aux objets de la db
        "FormPoste" : "",  # form non liée au template pour ajout d un nouveau poste
        "DicCreneaux" : "",  # dictionnaire des formes de creneau de l'evenement liées aux objets de la db
        "FormCreneau" : "",  # form non liée au template pour ajout d un nouveau creneau
        "Majeur" : check_majeur(request.user.date_de_naissance, evenement.debut.date()), # booleen précisant si le bénévole est majeur
        "EvtOuvertBenevoles" : inscription_ouvert(evenement.inscription_debut, evenement.inscription_fin) , # integer précisant si on est avant/dans/après la période de modification des creneaux
        "Text": text_template[language], # textes traduits 
    }
    print(data["Equipes"])
    print(data["equipes_avec_planning"])
    data["FormPlanning"] = PlanningForm(initial={'evenement': evenement, 'equipe': data["equipe_uuid"]})
    # recupere les uuid en POST, but est de tout gerer dans une seule page
    # et d'afficher les infos en fonction des POST recus :
    if request.method == "POST":

        # log les donnees post
        logger.info('##################### evenement ########################')
        logger.info('#   données POST passées: ')
        for key, value in request.POST.items():
            logger.info(f'#        POST -> {key} : {value}')
        logger.info('#########################################################')

        uuid_evenement = request.POST.get('evenement')
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

        # admin change un objet de l'evenement
        if  any(x in request.POST for x in ['creneau_modifier', 'creneau_ajouter', 'creneau_supprimer']):
            data["Form"]=forms_creneau(request)
        if any(x in request.POST for x in ['poste_modifier', 'poste_ajouter','poste_supprimer']):
            data["Form"]=forms_poste(request)
        if any(x in request.POST for x in ['planning_modifier', 'planning_ajouter', 'planning_supprimer']):
            data["Form"]=forms_planning(request)
        if any(x in request.POST for x in ['equipe_modifier', 'equipe_ajouter', 'equipe_supprimer']):
            data["Form"]=forms_equipe(request)

        if 'reste_sur_plannings_page' in request.POST:
            # admin dans gestion des equipes planning, il y reste
            data["PlanningRange"] = planning_range(evenement.debut, evenement.fin, 30)
        else:
            # dans equipe
            if request.POST.get('equipe'):  # selection d'une équipe
                data["equipe_uuid"] = request.POST.get('equipe')  
                # UUID equipe selectionnée
                if request.POST.get('planning') and not request.POST.get('planning_supprimer'):  
                    # selection d'un planning
                    data["planning_uuid"] = request.POST.get('planning')
                    data["Planning"] = Planning.objects.get(UUID=data["planning_uuid"])  # planning selectionnée
                    # instances de form poste & creneau liées : modifs & suppression & liste des postes
                    data["PlanningRange"] = planning_range(Planning.objects.get(UUID=request.POST.get('planning')).debut,
                                                        Planning.objects.get(UUID=request.POST.get('planning')).fin,
                                                        Planning.objects.get(UUID=request.POST.get('planning')).pas)
                    # retourne les creneaux d'un evenement sur une plage et sur tous les plannings 
                    # permet de savoir si le user est occupe sur la plage 
                    data["Creneaux_plage"] = \
                        tous_creneaux_entre_2_heures(Planning.objects.get(UUID=request.POST.get('planning')).debut,
                                                        Planning.objects.get(UUID=request.POST.get('planning')).fin,
                                                        uuid_evenement)
                else:
                    # selection d'une equipe uniquement, pas de planning, on affiche le premier planning en date
                    try:
                        data["Planning"] = Planning.objects.filter(equipe_id=request.POST.get('equipe')).order_by('debut').first()
                        data["planning_uuid"] = data["Planning"].UUID
                        # recupère les heures du planning
                        data["PlanningRange"] = planning_range(Planning.objects.get(UUID=data["planning_uuid"]).debut,
                                                        Planning.objects.get(UUID=data["planning_uuid"]).fin,
                                                        Planning.objects.get(UUID=data["planning_uuid"]).pas)
                    except:
                        logger.info(f'equipe sans planning: {request.POST.get("equipe")} ')
                        data["planning_perso"] = "oui"
                        data["PlanningRange"] = planning_range(evenement.debut, evenement.fin, 30)

                # envoi les forms au template
                if data["planning_uuid"]:
                    planning = Planning.objects.get(UUID=data["planning_uuid"])
                    data["DicPostes"] = dic_forms_postes(planning)
                    data["DicCreneaux"] = dic_forms_creneaux(request, planning)
                    #data["Postes"] = planning.poste_set.order_by('nom')  # objets postes du planning
                    #data["Creneaux"] = planning.creneau_set.order_by('nom')  # objets creneaux du planning
                    data["PostesCreneaux"] = postes_creneaux(planning)

            elif not request.POST.get('equipe'):  
                # selection d'un evenement uniquement
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
            
            # on envoie la form non liée au template pour ajout d un nouveau poste
            data["FormPoste"] = PosteForm(initial={'evenement': evenement,
                                                'equipe': data["equipe_uuid"],
                                                'planning': data["planning_uuid"]})
                            
            # on envoie la form non liée au template pour ajout d un nouveau creneau
            # si pas de creneau selectionné : type = "", sinon type = "creneau" ou "benevole" 
            # logger.info('POST TYPE : {}'.format(request.POST.get('type')))
            data["FormCreneau"] = CreneauForm(initial={'evenement': evenement,
                                                    'equipe': data["equipe_uuid"],
                                                    'planning': data["planning_uuid"],
                                                    'id_benevole': ProfileBenevole.UUID},
                                            pas_creneau=planning_retourne_pas(request),
                                            planning_uuid=request.POST.get('planning'),
                                            poste_uuid=request.POST.get('poste'),
                                            benevole_uuid=request.POST.get('benevole'),
                                            personne_connectee=request.user,
                                            evenement=uuid_evenement,
                                            type=request.POST.get('type'), )
            # si le benevole appuie sur le bouton "mon planning"
            if request.POST.get('planning_perso'):
                data["planning_perso"] = "oui"
                data["PlanningRange"] = planning_range(evenement.debut,
                                                    evenement.fin,
                                                    30)
            if request.POST.get('planning_global'):
                data["planning_global"] = "oui"

    # si pas de données post, affiche le planning global de l'evenement
    else:
        data["PlanningRange"] = planning_range(evenement.debut,
                                            evenement.fin,
                                            30)
    # check des roles de user sur l evenement:
    logger.info('#########################################################')
    logger.info('#   utilisateur connecté: ')
    logger.info(f'#        {request.user.first_name} {request.user.last_name} ')
    logger.info('#   roles : ')

    # groupes/roles de l utilisateur
    if not request.method == "POST" or (request.POST.get('evenement') and not request.POST.get('equipe') and not request.POST.get('planning'))or request.POST.get('planning') and request.POST.get('planning_supprimer'):
        # pas de POST ou page evenement ou le planning vient d 'etre supprimé 
        RolesUtilisateur = ListeGroupesUserFiltree(request, "ev", evenement)
    elif request.POST.get('equipe') and not request.POST.get('planning'):
        # equipe et pas de planning
        RolesUtilisateur = ListeGroupesUserFiltree(request, "eq", Equipe.objects.get(UUID=request.POST.get('equipe')))
    elif request.POST.get('planning') and not request.POST.get('planning_supprimer'):
        # planning et pas supprimé
        RolesUtilisateur = ListeGroupesUserFiltree(request, "plan", Planning.objects.get(UUID=request.POST.get('planning')))
    else:
        # le benevole arrive sur la page de l evenement
        RolesUtilisateur = ListeGroupesUserFiltree(request, "ev", evenement)
    try:
        for role in RolesUtilisateur:
            data[role] = "oui" # passe les roles 
    except:
        logger.error('erreur dans les RolesUtilisateur')
    logger.info('#########################################################')     
                                           
    logger.info(f'*** Fin traitement view : {datetime.now()}')
    return render(request, "evenement/base_evenement.html", data)


@login_required(login_url='login')
def CreneauFetch(request):
    """
        view pour requete javascript fetch 
        retourne un form creneau
        le but est de ne pas avoir a charger un modal spécifique par creneau affiché
    """
    logger.info(request)
    if request.method == "POST":
        logger.info('##################### CreneauFetch ######################')
        for key, value in request.POST.items():
            logger.info(f'#        POST -> {key} : {value}')
        logger.info('#########################################################')
        
        if request.POST.get('creneau_affiche') == 'form' :
            creneau = CreneauForm(personne_connectee=request.user, 
                                type="creneau",
                                evenement=request.POST.get('evenement_uuid'),
                                instance=Creneau.objects.get(UUID=request.POST.get('creneau_uuid')))
            return HttpResponse(creneau.as_table(), content_type="text/plain")
            # return JsonResponse({'creneau_form' : creneau }, safe=False)
        elif request.POST.get('creneau_affiche') == 'json':
            creneau = Creneau.objects.filter(UUID=request.POST.get('creneau_uuid')).values()
            creneau_obj = Creneau.objects.get(UUID=request.POST.get('creneau_uuid'))
            poste = Poste.objects.get(UUID=creneau_obj.poste_id).nom
            planning = Planning.objects.get(UUID=creneau_obj.planning_id).nom
            equipe = Equipe.objects.get(UUID=creneau_obj.equipe_id).nom
            try : 
                benevole_nom = ProfileBenevole.objects.get(UUID=creneau_obj.benevole_id).personne.last_name
                benevole_pre = ProfileBenevole.objects.get(UUID=creneau_obj.benevole_id).personne.first_name
                benevole= f"{benevole_nom.upper()} {benevole_pre.title()}"
            except:
                benevole = "Libre"
            context = {
                'creneau' : list(creneau)[0],
                'poste_nom' : poste,
                'planning_nom': planning,
                'equipe_nom' : equipe,
                'benevole_nom' : benevole,
            }
            return JsonResponse(context, safe=False) 

@login_required(login_url='login')
def PlanningFetch(request):
    """
        view pour requete javascript fetch 
        retourne un form planning
        le but est de ne pas avoir a charger un modal spécifique par planning affiché
    """
    logger.info(request)
    if request.method == "POST":
        logger.info('##################### PlanningFetch ######################')
        for key, value in request.POST.items():
            logger.info(f'#        POST -> {key} : {value}')
        logger.info('#########################################################')
        if request.POST.get('planning_affiche') == 'form' :
            planning = PlanningForm(instance=Planning.objects.get(UUID=request.POST.get('planning_uuid')))
            return HttpResponse(planning.as_table(), content_type="text/plain")
        elif request.POST.get('planning_affiche') == 'json':
            planning = Planning.objects.filter(UUID=request.POST.get('planning_uuid')).values()
            equipe_nom = Equipe.objects.get(planning__UUID=request.POST.get('planning_uuid')).nom
            logger.info(equipe_nom)
            context = {
                'planning' : list(planning)[0],
                'equipe_nom' : equipe_nom,
            }
            return JsonResponse(context, safe=False) 