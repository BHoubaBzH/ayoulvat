from datetime import timedelta
from django.db.models import Q

from evenement.forms import EquipeForm, PlanningForm, PosteForm, CreneauForm
from evenement.models import Evenement, Equipe, Planning, Poste, Creneau
from benevole.models import ProfileBenevole
from .generic import envoi_courriel

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

def dic_forms_plannings(uuid_evenement):
    """
        entree:
            l'uid de l'evenement
        sortie:
            dictionnaire des forms planning: key: UUID / val: form
    """
    # cree dans la page toutes nos form pour le planning
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

def PlanningCreneauxDispo(plans):
    """
        entree : 
            queryset de plannings 
        sortie :
            dictionnaire : UUID planning, nb creneau dispo dans le planning
    """
    dic_out = {}
    for plan in plans:
        #logger.info(' planning UUID : {}'.format(plan.UUID))
        nb_dispo = Creneau.objects.filter(Q(planning_id=plan.UUID), Q(benevole_id__isnull=True)).count()
        #logger.info('                      : {}'.format(nb_dispo))
        dic_out[plan.UUID] = nb_dispo
    return dic_out

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

def dic_forms_creneaux(request, planning, RolesUtilisateur):
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
    creneaux = planning.creneau_set.select_related(
        'poste', 'planning', 'equipe', 'evenement', 'benevole__personne'
    ).prefetch_related(
        'benevole__BenevolesEvenement'
    )
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
                                  personne_connectee_roles=RolesUtilisateur,
                                  type=creneau._meta.get_field('type').value_from_object(creneau), )
        dic_creneaux_init[creneau.UUID] = formcreneau  # dictionnaire des forms: key: UUID / val: form
    return dic_creneaux_init