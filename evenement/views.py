from datetime import timedelta

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404
from django.utils.timesince import timesince
from django.forms import formset_factory

from evenement.forms import PosteForm, CreneauForm
from evenement.models import Evenement, Equipe, Planning, Poste, Creneau
from benevole.models import ProfileBenevole, Personne, AssoOrigine, ProfileResponsable, ProfileOrganisateur


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


def forms_postes(request, data, the_planning):
    """
        entree:
            le planning contenant les postes
            la requete (contenant les infos POST)
        sortie:
            null
        gère également la modification et la suppression de poste en fonction du contenu de POST
    """
    # sauvegarde notre form modifée envoyée en POST
    if 'poste_modifier' in request.POST:
        # form en lien avec l objet basé sur model et pk UUID_poste
        formposte = PosteForm(request.POST,
                              instance=Poste.objects.get(UUID_poste=request.POST.get('poste')))
        if formposte.is_valid():
            formposte.save()
    # sauvegarde de notre nouvelle form envoyée en POST
    if 'poste_ajouter' in request.POST:
        formposte = PosteForm(request.POST)
        if formposte.is_valid():
            formposte.save()
            print('poste ajouté')
    # suppression du poste
    if request.POST.get('poste_supprimer'):
        print('poste {} supprimé'.format(Poste.objects.filter(UUID_poste=request.POST.get('poste_supprimer'))))
        Poste.objects.filter(UUID_poste=request.POST.get('poste_supprimer')).delete()

    # cree dans la page toutes nos from pour les postes du planing
    dic_postes_init = {}  # dictionnaire des forms
                          # key : UUID postes
                          # val : liste avec forms de postes initialisées objet db lié
    # parcours les postes du planning dans la base
    for poste in Poste.objects.filter(planning_id=the_planning):
        # form en lien avec l objet basé sur model et pk UUID_poste
        formposte = PosteForm(instance=Poste.objects.get(UUID_poste=poste.UUID_poste))
        dic_postes_init[poste.UUID_poste] = formposte  # dictionnaire des forms
        # print (' poste UUID : {1} form : {0}'.format(formposte, poste.UUID_poste))
    data["DicPostes"] = dic_postes_init
    return

def forms_creneaux(request, data, postes):
    """
        entree:
            les postes affichés
            la requete (contenant les infos POST)
        sortie:
            null
        gère également la modification et la suppression de creneaux en fonction du contenu de POST
    """
    if 'creneau_modifier' in request.POST:
        # form en lien avec l objet basé sur model et pk UUID_poste
        # print('creneau : {}'.format(request.POST.get('uuid_creneau')))
        formcreneau = CreneauForm(request.POST,
                                  instance=Creneau.objects.get(UUID_creneau=request.POST.get('creneau')))
        print(formcreneau['benevole'])
        print(formcreneau.errors)
        if formcreneau.is_valid():
            formcreneau.save()
    if 'creneau_ajouter' in request.POST:
        formcreneau = CreneauForm(request.POST)
        if formcreneau.is_valid():
            formcreneau.save()
            print('poste ajouté')
    if request.POST.get('creneau_supprimer'):
        print('creneau {} supprimé'.format(Creneau.objects.filter(UUID_creneau=request.POST.get('creneau_supprimer'))))
        Creneau.objects.filter(UUID_creneau=request.POST.get('creneau_supprimer')).delete()
    # cree dans la page toutes nos from pour les creneaux du planing
    dic_creneaux_init = {}  # dictionnaire des forms
                            # key : UUID postes
                            # val : liste avec forms de postes initialisées objet db lié
    # parcours les postes du planning dans la base
    for creneau in Creneau.objects.filter(poste_id__in=postes):       # liste des creneaux des postes du planning
        # form en lien avec l objet basé sur model et pk UUID_poste
        formcreneau = CreneauForm(instance=Creneau.objects.get(UUID_creneau=creneau.UUID_creneau))
        dic_creneaux_init[creneau.UUID_creneau] = formcreneau  # dictionnaire des forms
        # print(' creneau UUID : {1} form : {0}'.format(formcreneau, creneau.UUID_creneau))
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
    uuid_asso = request.session.get('uuid_association')

    data = {
        # on filtre les évènements sur ceux de l'asso uniquement
        "Evenements": Evenement.objects.filter(association_id=uuid_asso),
    }
    return render(request, "evenement/evenements_liste.html", data)


@login_required(login_url='login')
@permission_required('evenement.view_evenement', login_url='login')
def evenement(request, uuid_evenement):
    """
        page d'un evenement
    """
    the_equipe = ''
    the_planning = ''
    # store dans la session le uuid de l'evenement
    # il apparait dans l'url pour pouvir donner le liens aux bénévoles par la suite
    request.session['uuid_evenement'] = uuid_evenement

    # on construit nos objet avec l'uuid de l'evenement
    evenement = Evenement.objects.get(UUID_evenement=uuid_evenement)
    equipes = Equipe.objects.filter(evenement_id=uuid_evenement)

    data = {
        "Evenement": evenement,
        "Equipes": equipes,
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
            data["equipe"] = the_equipe
            data["Equipe"] = Equipe.objects.get(UUID_equipe=the_equipe)  # equipe selectionnée
            data["Plannings"] = Planning.objects.filter(equipe_id=the_equipe).order_by('debut')  # plannings de l'equipe
        if request.POST.get('planning'): # selection d'un planning
            the_planning = request.POST.get('planning')
            data["planning"] = the_planning
            planning = Planning.objects.get(UUID_planning=the_planning)
            data["Planning"] = planning  # planning selectionnée
            postes = Poste.objects.filter(planning_id=the_planning).order_by('nom')
            data["Postes"] = postes  # postes du planning
            # instances de form poste & creneau : sauvegarde modifs & suppression & liste des postes
            forms_postes(request, data, the_planning)
            forms_creneaux(request, data, postes)

            # données formatées du planning
            data["PlanningRange"] = planning_range(planning.debut, planning.fin, planning.pas)
            crenos = []
            for po in postes:
                crenos.append(po.UUID_poste)        # crenos : liste des creneaux du planning par poste
            creneaux = Creneau.objects.filter(poste_id__in=crenos)       # liste des creneaux des postes du planning
            try:
                data["Creneaux"] = creneaux
            except:
                print('###### pas de creneaux sur ce planning')

        if request.POST.get('poste'): # selection d'un poste
            the_poste = request.POST.get('poste')
            data["poste"] = the_poste
        if request.POST.get('creneau'): # selection d'un poste
            the_creneau = request.POST.get('creneau')
            data["creneau"] = the_creneau

        # on envoie la form non liée au template pour ajout d un nouveau poste
        data["FormPoste"] = PosteForm(initial={'evenement': evenement,
                                               'equipe': the_equipe,
                                               'planning': the_planning})
        # on envoie la form au template pour ajout d un nouveau poste
        data["FormCreneau"] = CreneauForm(initial={'evenement': evenement,
                                                   'equipe': the_equipe,
                                                   'planning': the_planning})

    '''
    # on se garde la possibilité d'afficher sur une granulometrie par poste en plus de planning  
    if uuid_poste:  # selection d'un poste
        poste = Poste.objects.get(UUID_poste=uuid_poste)
        creneaux = Creneau.objects.filter(poste_id=uuid_poste)
        data["Poste"] = poste  # recupere le poste selectionnée
        data["Creneaux"] = creneaux.order_by('debut')  # recupere les creneaux du poste
    '''
    return render(request, "evenement/evenement.html", data)
