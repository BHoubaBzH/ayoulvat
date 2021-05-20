from datetime import timedelta

from django.contrib.auth.decorators import login_required, permission_required
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from evenement.forms import EquipeForm, PlanningForm, PosteForm, CreneauForm
from evenement.models import Evenement, Equipe, Planning, Poste, Creneau
from benevole.models import ProfileBenevole, Personne, AssoOrigine, ProfileResponsable, ProfileOrganisateur
from association.models import Association


################################################
#             fonctions
################################################

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
    # print('###### planning : {0} - {1}'.format(debut, fin))
    dates_heures = {}
    while debut <= fin:
        # print('date : {}'.format(debut))
        date = debut.strftime("%Y-%m-%d-%H%M")
        heure = debut.strftime("%H:%M")
        dates_heures[date] = [heure, debut]
        debut += timedelta(minutes=delta)
    return dates_heures


def planning_retourne_pas(request):
    """
        entree:
            POST request
        sortie:
            pas_value : pas d'incrément du planning
        recuperer le pas du planning principalement pour les creneau et le choix des heures
    """
    if 'planning' in request.POST:
        # retrouve le pas du planning à partir des infos du creneau
        Plan = Planning.objects.get(UUID=request.POST.get('planning'))
        pas_value = Plan._meta.get_field('pas').value_from_object(Plan)
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
        # print(' creno : {}'.format(creno.nom))
    return crenos_out


def forms_equipe(request, data, uuid_evenement):
    """
        entree:
            la requete (contenant les infos POST)
            l'objet data renvoyé au template
            l'uid de l'evenement
        sortie:
            null
        gère la création, modification et suppression des equipes en fonction du contenu de POST
    """
    if any(x in request.POST for x in ['equipe_modifier', 'equipe_ajouter']):
        if 'equipe_modifier' in request.POST:
            formequipe = EquipeForm(request.POST,
                                  instance=Equipe.objects.get(UUID=request.POST.get('equipe')))
        # nouvel objet en base
        if 'equipe_ajouter' in request.POST:
            formequipe = EquipeForm(request.POST)
            print(formequipe.errors)
        if formequipe.is_valid():
            print('equipe modifié ou ajouté')
            formequipe.save()

    if request.POST.get('equipe_supprimer'):
        Equipe.objects.filter(UUID=request.POST.get('equipe_supprimer')).delete()

    # cree dans la page toutes nos from pour les equipes
    dic_equipe_init = {}  # dictionnaire des forms
    # key : UUID postes
    # val : form de poste initialisée objet db lié
    # parcours les equipes de l'evenement dans la base
    for equipe in Equipe.objects.filter(evenement_id=uuid_evenement):
        # form en lien avec l objet basé sur model et pk UUID equipe
        formequipe = EquipeForm(instance=Equipe.objects.get(UUID=equipe.UUID))
        dic_equipe_init[equipe.UUID] = formequipe  # dictionnaire des forms
        # print (' equipe UUID : {}'.format(equipe.UUID))
    return dic_equipe_init

def forms_planning(request, data, uuid_evenement):
    """
        entree:
            la requete (contenant les infos POST)
            l'objet data renvoyé au template
            l'uid de l'evenement
        sortie:
            null
        gère la création, modification et suppression des plannings en fonction du contenu de POST
    """
    if any(x in request.POST for x in ['planning_modifier', 'planning_ajouter']):
        if 'planning_modifier' in request.POST:
            formplanning = PlanningForm(request.POST,
                                  instance=Planning.objects.get(UUID=request.POST.get('planning')))
        # nouvel objet en base
        if 'planning_ajouter' in request.POST:
            formplanning = PlanningForm(request.POST)
            print(formplanning.errors)
        if formplanning.is_valid():
            print('planning modifié ou ajouté')
            formplanning.save()

    if request.POST.get('planning_supprimer'):
        Planning.objects.filter(UUID=request.POST.get('planning_supprimer')).delete()

    # cree dans la page toutes nos from pour les postes du planning
    dic_planning_init = {}  # dictionnaire des forms
    # key : UUID postes
    # val : form de poste initialisée objet db lié
    # parcours les plannings de l'evenement dans la base
    for planning in Planning.objects.filter(evenement_id=uuid_evenement):
        # form en lien avec l objet basé sur model et pk UUID equipe
        formplanning = PlanningForm(instance=Planning.objects.get(UUID=planning.UUID))
        dic_planning_init[planning.UUID] = formplanning  # dictionnaire des forms
        # print (' planning UUID : {}'.format(planning.UUID))
    return dic_planning_init

def forms_postes(request, data, uuid_evenement):
    """
        entree:
            la requete (contenant les infos POST)
            l'objet data renvoyé au template
            l'uid de l'evenement
        sortie:
            dictionnaire des forms postes: key: UUID / val: form
        gère la création, modification et suppression de poste en fonction du contenu de POST
    """
    # sauvegarde notre form modifée et crée envoyée en POST
    if any(x in request.POST for x in ['poste_modifier', 'poste_ajouter']):
        # form en lien avec l objet basé sur model et pk UUID poste
        if 'poste_modifier' in request.POST:
            formposte = PosteForm(request.POST,
                                  instance=Poste.objects.get(UUID=request.POST.get('poste')))
        # nouvel objet en base
        if 'poste_ajouter' in request.POST: 
            formposte = PosteForm(request.POST)
        if formposte.is_valid():
            formposte.save()
            print('poste modifié ou ajouté')

    # suppression du poste
    if request.POST.get('poste_supprimer'):
        print('poste {} supprimé'.format(Poste.objects.filter(UUID=request.POST.get('poste_supprimer'))))
        Poste.objects.filter(UUID=request.POST.get('poste_supprimer')).delete()

    # cree dans la page toutes nos from pour les postes du planning
    dic_postes_init = {}  # dictionnaire des forms
    # key : UUID postes
    # val : form de poste initialisée objet db lié
    # parcours les postes de l'evenement dans la base
    for poste in Poste.objects.filter(evenement_id=uuid_evenement):
        # form en lien avec l objet basé sur model et pk UUID poste
        formposte = PosteForm(instance=Poste.objects.get(UUID=poste.UUID))
        dic_postes_init[poste.UUID] = formposte  # dictionnaire des forms
        # print (' poste UUID : {1} form : {0}'.format(formposte, poste.UUID))
    return dic_postes_init


def forms_creneaux(request, data, uuid_evenement):
    """
        entree:
            la requete (contenant les infos POST)
            l'objet data renvoyé au template
            l'uid de l'evenement
        sortie:
            dictionnaire des forms creneaux: key: UUID / val: form
        gère la création, modification et suppression de creneaux en fonction du contenu de POST
    """
    if any(x in request.POST for x in ['creneau_modifier', 'creneau_ajouter']):
        # form en lien avec l objet basé sur model et pk UUID creneau
        if 'creneau_modifier' in request.POST:
            formcreneau = CreneauForm(request.POST,
                                      instance=Creneau.objects.get(UUID=request.POST.get('creneau')),
                                      pas_creneau=planning_retourne_pas(request),
                                      planning_uuid=request.POST.get('planning'),
                                      poste_uuid=request.POST.get('poste'),
                                      benevole_uuid=request.POST.get('benevole'),
                                      personne_connectee=request.user,
                                      type=request.POST.get('type'), )
        # nouvel objet en base
        if 'creneau_ajouter' in request.POST:
            formcreneau = CreneauForm(request.POST,
                                      pas_creneau=planning_retourne_pas(request),
                                      planning_uuid=request.POST.get('planning'),
                                      poste_uuid=request.POST.get('poste'),
                                      benevole_uuid=request.POST.get('benevole'),
                                      personne_connectee=request.user,
                                      type=request.POST.get('type'), )
        # print(formcreneau['benevole'])
        print(formcreneau.errors)
        if formcreneau.is_valid():
            print('creneau modifié ou ajouté')
            formcreneau.save()

    if request.POST.get('creneau_supprimer'):
        print('creneau {} supprimé'.format(Creneau.objects.filter(UUID=request.POST.get('creneau_supprimer'))))
        Creneau.objects.filter(UUID=request.POST.get('creneau_supprimer')).delete()

    # cree dans la page toutes nos from pour les creneaux de l' evenement
    dic_creneaux_init = {}  # dictionnaire des forms
    # key : UUID postes
    # val : form de creneau initialisée objet db lié
    # parcours les creneaux de l'evenement dans la base
    for creneau in Creneau.objects.filter(evenement_id=uuid_evenement):  # liste des creneaux de l'evenement
        # form en lien avec l objet basé sur model et pk UUID creneau
        formcreneau = CreneauForm(instance=Creneau.objects.get(UUID=creneau.UUID),
                                  pas_creneau=planning_retourne_pas(request),
                                  planning_uuid=request.POST.get('planning'),
                                  poste_uuid=request.POST.get('poste'),
                                  benevole_uuid=request.POST.get('benevole'),
                                  personne_connectee=request.user,
                                  type=creneau._meta.get_field('type').value_from_object(creneau), )
        dic_creneaux_init[creneau.UUID] = formcreneau  # dictionnaire des forms: key: UUID / val: form
        # print(' creneau UUID : {1} form : {0}'.format(formcreneau, creneau.UUID))
    return dic_creneaux_init

################################################
#            views evenements
################################################
@login_required(login_url='login')
def liste_evenements(request):
    """
    liste les evenements de l'asso
    """
    # récupère dans la session l'uuid de l'association
    uuid_asso = request.session['uuid_association']
    association = Association.objects.get(UUID=uuid_asso)

    try:
        liste_evenements = Evenement.objects.filter(association_id=uuid_asso)
    except:
        print('Pas encore d evenement pour cette asso, voulez-vous en creer un?')

    data = {
        "Association": association,
        # on filtre les évènements sur ceux de l'asso uniquement
        "Evenements": liste_evenements,
    }
    return render(request, "evenement/evenement.html", data)


@login_required(login_url='login')
@permission_required('evenement.view_evenement', login_url='login')
def evenement(request, uuid_evenement):
    """
        page d'un evenement
    """
    # store dans la session le uuid de l'evenement
    # il apparait dans l'url pour pouvoir donner le liens directe aux bénévoles par la suite
    request.session['uuid_evenement'] = uuid_evenement.urn
    # récupère dans la session l'uuid de l'association, si on est passé par l'asso
    try:
        uuid_asso = request.session['uuid_association']
    except:  # sinon si on arrive direct sur l'url de l'evenement, on recupere uuid asso en base
        Ev = Evenement.objects.get(UUID=uuid_evenement)
        asso = Ev._meta.get_field('association_id')
        uuid_asso = asso.value_from_object(Ev)
        # on stock dans la session
        request.session['uuid_association'] = uuid_asso.urn

    # on construit nos objets a passer au template dans le dictionnaire data
    evenement = Evenement.objects.get(UUID=uuid_evenement)
    data = {
        "Association": Association.objects.get(UUID=uuid_asso),
        "Evenement": evenement,
        "Equipes": Equipe.objects.filter(evenement_id=uuid_evenement),  # objets equipes de l'evenement
        "Plannings": "",  # objets planning de l'evenement
        "Postes": "",  # objets postes de l'evenement
        "Creneaux": "",  # objets creneaux de l'evenement
        "Benevoles": "",  # objets benevoles de l'evenement

        "Planning": "",  # objet planning selectionné
        "Creneaux_plage": "",  # objets creneaux de l'evenement entre 2 dateheure
        "equipe_uuid": "",  # par defaut, pas d'equipe selectionée
        "planning_uuid": "",  # par defaut, pas de planning selectionée
        "PlanningRange": "",  # dictionnaire formaté des dates heures de l'objet selectionné
        
        "FormEquipe" : "", # form non liée au template pour ajout d une nouvelle equipe
        "DicEquipes" : "",
        "FormPlanning" : "", # form non liée au template pour ajout d un nouveau planning
        "DicPlannings" : "",
        "DicPostes" : "",  # dictionnaire des formes de poste de l'evenement liées aux objets de la db
        "FormPoste" : "",  # form non liée au template pour ajout d un nouveau poste
        "DicCreneaux" : "",  # dictionnaire des formes de creneau de l'evenement liées aux objets de la db
        "FormCreneau" : "",  # form non liée au template pour ajout d un nouveau creneau
    }

    # log les donnees post
    print('#########################################################')
    for key, value in request.POST.items():
        print('#        POST -> {0} : {1}'.format(key, value))
    print('#########################################################')

    # recupere les uuid en POST, but est de tout gerer dans une seule page
    # et d'afficher les infos en fonction des POST recus :
    if request.method == "POST":
        uuid_evenement = request.POST.get('evenement')
        # models des objets de l'evenement
        data["Postes"] = Poste.objects.filter(evenement_id=uuid_evenement).order_by('nom')
        data["Plannings"] = Planning.objects.filter(evenement_id=uuid_evenement).order_by('debut')
        data["Creneaux"] = Creneau.objects.filter(evenement_id=uuid_evenement)
        data["Benevoles"] = ProfileBenevole.objects.filter(BenevolesEvenement=uuid_evenement)
        if request.POST.get('equipe'):  # selection d'une équipe
            data["equipe_uuid"] = request.POST.get('equipe')  # UUID equipe selectionnée

        if request.POST.get('planning'):  # selection d'un planning
            data["planning_uuid"] = request.POST.get('planning')
            data["Planning"] = Planning.objects.get(UUID=request.POST.get('planning'))  # planning selectionnée
            # instances de form poste & creneau liées : modifs & suppression & liste des postes
            data["DicPostes"] = forms_postes(request, data, uuid_evenement)
            data["DicCreneaux"] = forms_creneaux(request, data, uuid_evenement)
            # heures formatées du planning
            data["PlanningRange"] = planning_range(Planning.objects.get(UUID=request.POST.get('planning')).debut,
                                                   Planning.objects.get(UUID=request.POST.get('planning')).fin,
                                                   Planning.objects.get(UUID=request.POST.get('planning')).pas)
            # retourne les creneaux d'un evenement sur une plage et sur tous les plannings :
            data["Creneaux_plage"] = \
                tous_creneaux_entre_2_heures(Planning.objects.get(UUID=request.POST.get('planning')).debut,
                                             Planning.objects.get(UUID=request.POST.get('planning')).fin,
                                             uuid_evenement)

        else:  # selection d'un evenement uniquement
            data["PlanningRange"] = planning_range(evenement.debut, evenement.fin, 30)


        data["DicEquipes"] = forms_equipe(request, data, uuid_evenement)
        data["FormEquipe"] = EquipeForm(initial={'evenement': evenement})
        data["DicPlannings"] = forms_planning(request, data, uuid_evenement)
        data["FormPlanning"] = PlanningForm(initial={'evenement': evenement,
                                                     'equipe': data["equipe_uuid"]})

        # on envoie la form non liée au template pour ajout d un nouveau poste
        data["FormPoste"] = PosteForm(initial={'evenement': evenement,
                                               'equipe': data["equipe_uuid"],
                                               'planning': data["planning_uuid"]})
                        
        # on envoie la form non liée au template pour ajout d un nouveau creneau
        # si pas de creneau selectionné : type = "", sinon type = "creneau" ou "benevole" 
        # print('POST TYPE : {}'.format(request.POST.get('type')))
        data["FormCreneau"] = CreneauForm(initial={'evenement': evenement,
                                                   'equipe': data["equipe_uuid"],
                                                   'planning': data["planning_uuid"],
                                                   'id_benevole': ProfileBenevole.UUID},
                                          pas_creneau=planning_retourne_pas(request),
                                          planning_uuid=request.POST.get('planning'),
                                          poste_uuid=request.POST.get('poste'),
                                          benevole_uuid=request.POST.get('benevole'),
                                          personne_connectee=request.user,
                                          type=request.POST.get('type'), )
                                        
    return render(request, "evenement/evenement.html", data)
