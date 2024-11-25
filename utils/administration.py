from datetime import date, timedelta
from django.db.models import Q
from django.http import HttpResponse
from django.contrib import messages

from utils.generic import *
from utils.evenement import *

from evenement.forms import EvenementForm, EvenementForm_organisateur, EquipeForm, PlanningForm, PosteForm, CreneauForm
from evenement.models import Creneau, Equipe, Poste, Planning, evenement_benevole_assopart
from benevole.models import ProfileBenevole, ProfileOrganisateur
from ayoulvat.languages import flash, language

import copy
from django.db import transaction

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

################################################
#            fonctions 
################################################

def creneaux_asso_part(creneaux):
    """
        entree:
            liste des creneaux
        sortie:
            dictionnaire 
                creneaux : asso part du benevole
    """
    out = {}
    for creneau in creneaux:
        if creneau.benevole:
            out[creneau] = evenement_benevole_assopart.objects.get(
                evenement = creneau.evenement,
                profilebenevole = creneau.benevole
                ).asso_part
        else:
            out[creneau] = ""
    return out


def evenement_orga_edite(request):  
    """
        entree:
            la requete (contenant les infos POST)
        sortie:
            None
        gère la modification d un evenement
    """
    formevenement = EvenementForm_organisateur(request.POST,instance=Evenement.objects.get(UUID=request.POST.get('evenement_edite')))
    logger.info(formevenement.errors)
    if formevenement.is_valid():
        messages.success(request, flash[language]['event_mod_success'])
        formevenement.save()
    else:
        messages.error(request, flash[language]['event_mod_error'])

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
        return formequipe

    if request.POST.get('equipe_supprimer'):
        Equipe.objects.filter(UUID=request.POST.get('equipe_supprimer')).delete()

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
        # creation objet en base
        if 'planning_ajouter' in request.POST:
            formplanning = PlanningForm(request.POST)
            if formplanning.is_valid():
                messages.success(request, flash[language]['plan_new_success'])
                logger.info('planning modifié ou ajouté')
                formplanning.save()
            else:
                messages.error(request, flash[language]['plan_new_error'])
                logger.warning(f'erreur dans la form : {formplanning.errors}')

    if request.POST.get('planning_supprimer'):
        plan_supp = Planning.objects.get(UUID=request.POST.get('planning_supprimer'))
        logger.warn(f'planning supprimer : {plan_supp}')
        if not plan_supp.creneau_set.all():
            plan_supp.delete()
            messages.success(request, flash[language]['plan_sup_success'])
        else :
            messages.error(request, flash[language]['plan_sup_error'])
    return formplanning        


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

def forms_creneau(request, RolesUtilisateur):
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
                                      personne_connectee_roles=RolesUtilisateur,
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
                                      personne_connectee_roles=RolesUtilisateur,
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

def total_heures_benevoles(creneaux):
    """ total d'heures de bénévolat sur l'évènement retourne un timedelta """
    total = timedelta(0, 0, 0, 0)
    for c in creneaux:
        if c.benevole:
            c_duree = c.fin - c.debut
            total += c_duree
    return total

def liste_benevoles_age_creneaux_assopart(evt, benevoles):
    """ input queryset des benevoles
        out dictionnaire: objet benevole - (age, nb creneaux, asso partenaire) """
    out={}
    logger.info(f'nb benevoles : {benevoles.count()}')
    for benevole in benevoles: 
        age=date.today().year - benevole.personne.date_de_naissance.year - ((date.today().month, date.today().day) < \
                        (benevole.personne.date_de_naissance.month, benevole.personne.date_de_naissance.day))
        try:
            creneaux=benevole.BenevolesCreneau.filter(evenement=evt)
            nbcreneaux=creneaux.count()
        except:
            nbcreneaux=0
        # calcul du nb heures par benevole
        nbheures = 0
        for creneau in creneaux:
            td_h = (creneau.fin - creneau.debut).total_seconds() / 3600
            nbheures = nbheures + td_h
        try:
            asso=evenement_benevole_assopart.objects.select_related('asso_part').get(Q(evenement=evt), Q(profilebenevole=benevole)).asso_part
        except:
            asso='None'
        out[benevole]=(
            age,
            nbcreneaux,
            nbheures,
            asso,
        )
    return out 

def nb_benevoles_par_asso(list_assos, evt):
    """ returne un dictionnaire de nombre de bénévole par asso sur l evenement"""
    dic = {}
    for asso in list_assos:
        dic[asso] = evenement_benevole_assopart.objects.filter(Q(asso_part=asso),Q(evenement=evt)).count()
    # on force le choix d asso part maintenant, donc plus utile normalement 
    # dic['Sans association'] = evenement_benevole_assopart.objects.filter(Q(asso_part=None),Q(evenement=evt)).count()
    dic ={k: v for k, v in sorted(dic.items(), key=lambda x: x[1], reverse=True)}
    return dic

def nb_evenements_par_asso(list_assos):
    """ returne un dictionnaire de nombre d evenement par asso """
    dic = {}
    for asso in list_assos:
        dic[asso] = Evenement.objects.filter(association=asso).count()
    return dic


def plannings_occupation(contenants):
    """
        retoune le taux d'occupation par contenant 
        entree : queryset de contenants
        sortie : dictionnaire key : contenant , value : pourcentage occupation
    """
    occup = {}  
    for c in contenants:
        crens = Creneau.objects.filter(planning_id=c.UUID).count()
        crens_occup = Creneau.objects.filter(planning_id=c.UUID, benevole__isnull=False).count()
        pourcentage = (crens_occup / crens) * 100 if crens != 0 else 0
        occup[c] = round(pourcentage, 1)
    return occup

def equipes_occupation(contenants):
    """ 
        retoune le taux d'occupation par contenant 
        entree : queryset de contenants
        sortie : dictionnaire key : contenant , value : pourcentage occupation
    """
    occup = {}
    for c in contenants:
        crens = Creneau.objects.filter(equipe_id=c.UUID).count()
        crens_occup = Creneau.objects.filter(equipe_id=c.UUID, benevole__isnull=False).count()
        pourcentage = (crens_occup / crens) * 100 if crens != 0 else 0
        occup[c] = round(pourcentage, 1)
    return occup

def repartition_par_assos(creneaux):
    """ 
        retoune la répartition horaire par assos
        entree : queryset des creneaux de l evenement
        sortie : dictionnaire key : assos , pourcentage total et rangé du plus grand au plus petit
    """
    repart = dict()
    total = total_heures_benevoles(creneaux)

    for c in creneaux:
        try:
            # evenement, un benevole et une asso_prt de liés
            asso_du_creneau=evenement_benevole_assopart.objects.get(Q(evenement=c.evenement),Q(profilebenevole=c.benevole)).asso_part
            c_duree = c.fin - c.debut
            try:
                repart[asso_du_creneau.nom] += c_duree
            except:
                repart[asso_du_creneau.nom] = c_duree
        except:
            # pas de lien
            c_duree = c.fin - c.debut
            try:
                repart["sans association"] += c_duree
            except:
                repart["sans association"] = c_duree
    for rep, val in repart.items():
        repart[rep] = round(val / total *100, 1)
        # logger.info('{} : {}'.format(rep, repart[rep]))
    return dict(sorted(repart.items(), key=lambda item: item[1],reverse=True)) 

def emails_benevoles_evenement(evt):
    """
        sortie : liste emails des bénévoles ayant pris un créneau
    """
    listout = []
    for bene in evt.benevole.all():
        if Creneau.objects.filter(Q(benevole=bene),Q(evenement=evt)).count() != 0:
            listout.append(bene.personne.email)
    return set(listout)

def emails_benevoles_sans_creneaux(evt):
    """
        sortie : liste emails des bénévoles sans créneau
    """
    listout = []
    for bene in evt.benevole.all():
        if Creneau.objects.filter(Q(benevole=bene),Q(evenement=evt)).count() == 0:
            listout.append(bene.personne.email)
    return set(listout)

def emails_benevoles_un_creneau(evt):
    """
        sortie : liste emails des bénévoles ayant choisi un seul créneau
    """ 
    listout = []
    for bene in evt.benevole.all():
        if Creneau.objects.filter(Q(benevole=bene),Q(evenement=evt)).count() == 1:
            listout.append(bene.personne.email)
    return set(listout)

def emails_benevoles_par_equipe(evt):
    """
        sortie : dictionnaire de liste emails , clés : equipes
    """
    tabout = {}
    for equipe in list(Equipe.objects.filter(evenement=evt)):
        liste_emails = []
        for bene in ProfileBenevole.objects.filter(BenevolesCreneau__equipe=equipe).prefetch_related('BenevolesCreneau').select_related('personne'):
            email = bene.personne.email
            liste_emails.append(email)
            if liste_emails:
                tabout[equipe] = set(liste_emails)
    return tabout

def emails_benevoles_par_planning(evt):
    """
        sortie : dictionnaire de liste[ equipe, planning nom, [liste emails]] , clés : plannings
    """
    tabout = {}
    for planning in list(Planning.objects.filter(evenement=evt).order_by("debut")):
        liste_emails = []
        liste_planning = []
        #for bene in ProfileBenevole.objects.filter(BenevolesCreneau__planning=planning):
        for bene in ProfileBenevole.objects.filter(BenevolesCreneau__planning=planning).prefetch_related('BenevolesCreneau').select_related('personne'):
            email = bene.personne.email
            liste_emails.append(email)
        liste_planning.append(planning.equipe)
        liste_planning.append(planning.nom)
        liste_planning.append(set(liste_emails))
        tabout[planning] = liste_planning
    return tabout

def emails_responsables(evt):
    """
        sortie : liste emails des bénévoles responsables sur l'evenement
    """
    listout = []
    try:
        # referent de l asso
        listout.append(evt.association.referent.personne.email)
    except:
        pass
    for org in evt.organisateur.all():
        # organisateurs de l evenement
        listout.append(org.personne.email)
    for equ in evt.equipe_set.all():
        for res in equ.responsable.all():
            # responsables d equipes
            listout.append(res.personne.email)
    return set(listout) # set suprime les

def inscription_ouvert(debut, fin):
    """
        prend une date de debut et une date de fin en entree
        en sortie, un integer:
        0: si today avant la période
        1: si today dans la période
        2: si today après la période
    """
    if date.today() < debut:
        return 0
    elif debut <= date.today() <= fin:
        return 1
    else:
        return 2 
    
###
### fonctions pour la duplication d evenement
###

@transaction.atomic
def duplique_creneau(instance, clone_poste, delta_time=0, *args, **kwargs):
    ''' duplique un creneau '''
    #logger.info(f'              duplique creneau: {instance}')
    clone_creneau = copy.copy(instance)
    clone_creneau.pk = None
    if 'avec_benevoles' not in args[0]:
        # logger.info(f'do not keep benevole in slot param')
        clone_creneau.benevole = None # retire le benevole associé
    clone_creneau.evenement = clone_poste.evenement
    clone_creneau.equipe = clone_poste.equipe
    clone_creneau.planning = clone_poste.planning
    clone_creneau.poste = clone_poste
    clone_creneau.debut = clone_creneau.debut + delta_time
    clone_creneau.fin = clone_creneau.fin + delta_time
    clone_creneau.save()

@transaction.atomic
def duplique_poste(instance, clone_planning, delta_time=0, *args, **kwargs):
    ''' duplique un poste et les creneaux associés'''
    #logger.info(f'          duplique poste: {instance}')
    clone_poste = copy.copy(instance)
    clone_poste.pk = None
    clone_poste.evenement = clone_planning.evenement
    clone_poste.equipe = clone_planning.equipe
    clone_poste.planning = clone_planning
    clone_poste.save()

    for crs_object in instance._meta.related_objects:
        crs_name = crs_object.get_accessor_name()
        crs_manager = getattr(instance, crs_name)

        # duplique creneaux
        if (crs_name == 'creneau_set'):
            for cr_instance in crs_manager.all():
                if cr_instance.poste == instance:
                    duplique_creneau(cr_instance, clone_poste, delta_time, args[0])

@transaction.atomic
def duplique_planning(instance, clone_equipe, delta_time=0, *args, **kwargs):
    ''' duplique un planning et les postes, creneaux associés'''
    #logger.info(f'      duplique planning: {instance}')
    clone_planning = copy.copy(instance)
    clone_planning.pk = None
    clone_planning.evenement = clone_equipe.evenement
    clone_planning.equipe = clone_equipe
    clone_planning.debut = clone_planning.debut + delta_time
    clone_planning.fin = clone_planning.fin + delta_time
    clone_planning.save()

    for pos_object in instance._meta.related_objects:
        pos_name = pos_object.get_accessor_name()
        pos_manager = getattr(instance, pos_name)

        # duplique postes
        if (pos_name == 'poste_set'):
            for po_instance in pos_manager.all():
                if po_instance.planning == instance:
                    duplique_poste(po_instance, clone_planning, delta_time, args[0])

@transaction.atomic
def duplique_equipe(instance, clone_event, delta_time=0, *args, **kwargs):
    ''' duplique une équipe et les plannings, postes, creneaux associés'''
    #logger.info(f'  duplique equipe: {instance}')
    clone_equipe = copy.copy(instance)
    clone_equipe.pk = None
    clone_equipe.evenement = clone_event
    clone_equipe.save()

    for pls_object in instance._meta.related_objects:
        pls_name = pls_object.get_accessor_name()
        pls_manager = getattr(instance, pls_name)

        # duplique plannings
        if (pls_name == 'planning_set'):
            for pl_instance in pls_manager.all():
                if pl_instance.equipe == instance:
                    duplique_planning(pl_instance, clone_equipe, delta_time, args[0])

@transaction.atomic
def duplique_evenement(instance, delta_days=0, *args, **kwargs):
    ''' duplique un evenement et les equipes, plannings, postes, creneaux associés'''
    #logger.info(f'duplique evenement: {instance}')
    delta_time                      = timedelta(days=delta_days + 1)
    clone_event                     = copy.copy(instance)
    clone_event.pk                  = None
    clone_event.debut               = clone_event.debut + delta_time
    clone_event.fin                 = clone_event.fin + delta_time
    clone_event.inscription_debut   = clone_event.inscription_debut + delta_time
    clone_event.inscription_fin     = clone_event.inscription_fin + delta_time
    clone_event.save()

    # copi les liens organisateurs et assos parts
    clone_event.organisateur.set(instance.organisateur.all())
    clone_event.assopartenaire.set(instance.assopartenaire.all())

    for eqs_object in instance._meta.related_objects:
        eqs_name = eqs_object.get_accessor_name()
        eqs_manager = getattr(instance, eqs_name)

        # duplique equipes
        if (eqs_name == 'equipe_set'):
            for eq_instance in eqs_manager.all():
                duplique_equipe(eq_instance, clone_event, delta_time, args[0])

    if 'avec_benevoles' in args[0]:
        #logger.info('recopie les liens bénévoles - asso part - evenement sur ce  clone')
        benevoles = evenement_benevole_assopart.objects.filter(evenement=instance)
        for ben in benevoles:
            # recopie les bénévoles
            #logger.info(f'benevole : {ben}')
            clone_ben = copy.copy(ben)
            clone_ben.pk = None
            clone_ben.evenement = clone_event
            clone_ben.save()
            
