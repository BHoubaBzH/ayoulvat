from datetime import timedelta

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404

from evenement.forms import PosteForm, CreneauForm
from evenement.models import Evenement, Equipe, Planning, Poste, Creneau
from benevole.models import ProfileBenevole, Personne, AssoOrigine, ProfileResponsable, ProfileOrganisateur
from association.models import Association


################################################
##      fonctions
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
        Plan=Planning.objects.get(UUID=request.POST.get('planning'))
        pas=Plan._meta.get_field('pas')
        pas_value=pas.value_from_object(Plan)
    else:
        # pas possible normalement, on prévoit quand meme une valeur par défaut d une heure au pas
        pas_value=60
    return pas_value

def forms_postes(request, data, the_planning):
    """
        entree:
            la requete (contenant les infos POST)
            l'objet data renvoyé au template
            le planning contenant les postes
        sortie:
            null
        gère également la modification et la suppression de poste en fonction du contenu de POST
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

    # cree dans la page toutes nos from pour les postes du planing
    dic_postes_init = {}  # dictionnaire des forms
                          # key : UUID postes
                          # val : form de poste initialisée objet db lié
    # parcours les postes du planning dans la base
    for poste in Poste.objects.filter(planning_id=the_planning):
        # form en lien avec l objet basé sur model et pk UUID poste
        formposte = PosteForm(instance=Poste.objects.get(UUID=poste.UUID))
        dic_postes_init[poste.UUID] = formposte  # dictionnaire des forms
        # print (' poste UUID : {1} form : {0}'.format(formposte, poste.UUID))
    data["DicPostes"] = dic_postes_init
    return

def forms_creneaux(request, data, postes):
    """
        entree:
            la requete (contenant les infos POST)
            l'objet data renvoyé au template
            la liste des postes
        sortie:
            null
        gère également la modification et la suppression de creneaux en fonction du contenu de POST
    """
    if any(x in request.POST for x in ['creneau_modifier', 'creneau_ajouter']):
        # form en lien avec l objet basé sur model et pk UUID creneau
        if 'creneau_modifier' in request.POST:
            formcreneau = CreneauForm(request.POST,
                                      instance=Creneau.objects.get(UUID=request.POST.get('creneau')),
                                      pas_creneau=planning_retourne_pas(request),
                                      planning_uuid=request.POST.get('planning'),
                                      poste_uuid=request.POST.get('poste'),)
        # nouvel objet en base
        if 'creneau_ajouter' in request.POST:
            formcreneau = CreneauForm(request.POST,
                                      pas_creneau=planning_retourne_pas(request),
                                      planning_uuid=request.POST.get('planning'),
                                      poste_uuid=request.POST.get('poste'),)
        # print(formcreneau['benevole'])
        print(formcreneau.errors)
        if formcreneau.is_valid():
            print('creneau modifié ou ajouté')
            formcreneau.save()

    if request.POST.get('creneau_supprimer'):
        print('creneau {} supprimé'.format(Creneau.objects.filter(UUID=request.POST.get('creneau_supprimer'))))
        Creneau.objects.filter(UUID=request.POST.get('creneau_supprimer')).delete()

    # cree dans la page toutes nos from pour les creneaux du planing
    dic_creneaux_init = {}  # dictionnaire des forms
                            # key : UUID postes
                            # val : form de creneau initialisée objet db lié
    # parcours les creneaux du planning dans la base
    for creneau in Creneau.objects.filter(poste_id__in=postes):       # liste des creneaux des postes du planning
        # form en lien avec l objet basé sur model et pk UUID creneau
        formcreneau = CreneauForm(instance=Creneau.objects.get(UUID=creneau.UUID),
                                  pas_creneau=planning_retourne_pas(request),
                                  planning_uuid=request.POST.get('planning'),
                                  poste_uuid=request.POST.get('poste'),)
        dic_creneaux_init[creneau.UUID] = formcreneau  # dictionnaire des forms: key: UUID / val: form
        # print(' creneau UUID : {1} form : {0}'.format(formcreneau, creneau.UUID))
    data["DicCreneaux"] = dic_creneaux_init
    return

################################################
##      views evenements
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
    the_equipe = ''
    the_planning = ''
    # store dans la session le uuid de l'evenement
    # il apparait dans l'url pour pouvoir donner le liens aux bénévoles par la suite
    request.session['uuid_evenement'] = uuid_evenement.urn
    # récupère dans la session l'uuid de l'association, si on est passé par l'asso
    try:
        uuid_asso = request.session['uuid_association']
    except: # sinon si on arrive direct sur l'url de l'evenement, on recupere en base
        Ev = Evenement.objects.get(UUID=uuid_evenement)
        asso = Ev._meta.get_field('association_id')
        uuid_asso = asso.value_from_object(Ev)
        # on stock dans la session
        request.session['uuid_association'] = uuid_asso.urn

    # on construit nos objet avec l'uuid de l'evenement
    evenement = Evenement.objects.get(UUID=uuid_evenement)
    data = {
        "Association": Association.objects.get(UUID=uuid_asso),
        "Evenement": evenement,
        "Equipes": Equipe.objects.filter(evenement_id=uuid_evenement),
    }

    # log les donnees post
    print('#########################################################')
    for key, value in request.POST.items():
        print('#        POST -> {0} : {1}'.format(key, value))
    print('#########################################################')

    # recupere les uuid en POST, but est de tout gerer dans une seule page
    # et d'afficher les infos en fonction des POST recus :
    if request.method == "POST":
        if request.POST.get('equipe'):  # selection d'une équipe
            the_equipe = request.POST.get('equipe')
            data["equipe"] = the_equipe  # UUID equipe selectionnée
            # data["Equipe"] = Equipe.objects.filter(UUID=the_equipe)  # model equipe selectionnée
            data["Plannings"] = \
                Planning.objects.filter(equipe_id=the_equipe).order_by('debut')  # models de plannings de l'equipe
        else :  # selection d'un evènement mais pas d equipe, models de planning de l evenement
            data["Plannings"] = Planning.objects.filter(evenement_id=uuid_evenement).order_by('debut')
            # pour l'affichage du nom de creneau
            # on construit un dictionnaire key: uuid_equipe - val: nom equipe
            dict_nom_creneau = {}
            for Plan in Planning.objects.filter(evenement_id=uuid_evenement):
                key = Plan._meta.get_field('equipe_id')
                UUIDequipe= key.value_from_object(Plan)
                Eq = Equipe.objects.get(UUID=UUIDequipe)
                key = Eq._meta.get_field('nom')
                nomequipe = key.value_from_object(Eq)
                dict_nom_creneau[UUIDequipe] = nomequipe
            data["DicNomCreneau"] = dict_nom_creneau

        if request.POST.get('planning'): # selection d'un planning
            the_planning = request.POST.get('planning') # UUID planning
            data["planning"] = the_planning
            planning = Planning.objects.get(UUID=the_planning) # model planning
            data["Planning"] = planning  # planning selectionnée
            postes = Poste.objects.filter(planning_id=the_planning).order_by('nom') # models de postes du planning
            data["Postes"] = postes  # postes du planning
            benevoles = ProfileBenevole.objects.filter(BenevolesPlanning=the_planning) # models de benevoles du planning
            data["Benevoles"] = benevoles
            for benevole in benevoles:
                print ('benevoles : {}'.format(benevole))
            # instances de form poste & creneau : sauvegarde modifs & suppression & liste des postes
            forms_postes(request, data, the_planning)
            forms_creneaux(request, data, postes)

            # données formatées du planning créneaux
            data["PlanningRange"] = planning_range(planning.debut, planning.fin, planning.pas)
            crenos = []
            for po in postes:
                crenos.append(po.UUID)        # crenos : liste des creneaux du planning par poste
            # liste des creneaux des postes du planning
            creneaux = Creneau.objects.filter(poste_id__in=crenos, type="creneau")
            try:
                data["CreneauxCreneau"] = creneaux
            except:
                print('###### pas de creneaux sur ce planning')
            # liste des dispos bénévole sur le planning
            creneaux_benevole = Creneau.objects.filter(planning_id=planning, type="benevole")
            try:
                data["CreneauxBenevole"] = creneaux_benevole
            except:
                print('###### pas de dispo bénévole sur ce planning')
        elif request.POST.get('evenement'):  # selection d'un evenement uniquement
            data["PlanningRange"] = planning_range(evenement.debut, evenement.fin, 30)

        if request.POST.get('poste'): # selection d'un poste
            the_poste = request.POST.get('poste')
            data["poste"] = the_poste
        if request.POST.get('creneau'): # selection d'un creneau
            the_creneau = request.POST.get('creneau')
            data["creneau"] = the_creneau

    # on envoie la form non liée au template pour ajout d un nouveau poste
    data["FormPoste"] = PosteForm(initial={'evenement': evenement,
                                           'equipe': the_equipe,
                                           'planning': the_planning})
    # on envoie la form non liée au template pour ajout d un nouveau creneau
    data["FormCreneau"] = CreneauForm(initial={'evenement': evenement,
                                               'equipe': the_equipe,
                                               'planning': the_planning,
                                               'id_benevole': ProfileBenevole.UUID},
                                      pas_creneau=planning_retourne_pas(request),
                                      planning_uuid=request.POST.get('planning'),
                                      poste_uuid=request.POST.get('poste'),)

    return render(request, "evenement/evenement.html", data)
