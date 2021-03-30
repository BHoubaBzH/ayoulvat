import re
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.formats import localize

from evenement.models import Evenement, Equipe, Planning, Poste, Creneau


################################################
##      fonctions
################################################
def planning_range(debut, fin):
    '''
        retourne un dictionnaire des dates et heures par pas de 30 minutes
        dates pour les style unique et bien placer le creneau dans le ccs grid
        heures pour l'affichage
    '''
    print('###### planning : {0} - {1}'.format(debut, fin))
    dates_heures = {}
    while debut <= fin:
        date = debut.strftime("%Y-%m-%d-%H%M")
        heure = debut.strftime("%H:%M")
        dates_heures[date] = heure
        debut += timedelta(minutes=30)
    return dates_heures


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
def detail_evenement(request, uuid_evenement):
    """
    détails d'un evenement
    """
    uuid_equipe = ''
    uuid_planning = ''
    uuid_poste = ''
    # store dans la session le uuid de l'evenement
    request.session['uuid_evenement'] = uuid_evenement
    print('uuid evt : {}'.format(uuid_evenement))

    # on construit nos objet avec l'uuid de l'evenement
    evenement = Evenement.objects.get(UUID_evenement=uuid_evenement)
    equipes = Equipe.objects.filter(evenement_id=uuid_evenement)

    data = {
        "Evenement": evenement,
        "Equipes": equipes,
        "uuid_evenement": uuid_evenement,
    }

    # log les donnees post
    for key, value in request.POST.items():
        print('{0} : {1}'.format(key, value))

    # recupere les uuid en POST, but est de tout gerer dans une seule page:
    if request.POST.get('uuid_equipe'):
        uuid_equipe = request.POST.get('uuid_equipe')
        data["uuid_equipe"] = uuid_equipe
    if request.POST.get('uuid_planning'):
        uuid_planning = request.POST.get('uuid_planning')
        data["uuid_planning"] = uuid_planning
    if request.POST.get('uuid_poste'):
        uuid_poste = request.POST.get('uuid_poste')
        data["uuid_poste"] = uuid_poste

    if uuid_equipe:  # selection d'une équipe
        equipe = Equipe.objects.get(UUID_equipe=uuid_equipe)
        plannings = Planning.objects.filter(equipe_id=uuid_equipe).order_by('debut')
        data["Equipe"] = equipe  # recupere l'equipe selectionnée
        data["Plannings"] = plannings  # recupere les plannings de l'equipe
    if uuid_planning:  # selection d'un planning
        planning = Planning.objects.get(UUID_planning=uuid_planning)
        postes = Poste.objects.filter(planning_id=uuid_planning).order_by('nom')
        data["Planning"] = planning  # recupere le planning selectionnée
        data["Postes"] = postes  # recupere les postes du planning
        data["PlanningRange"] = planning_range(planning.debut, planning.fin) # données formatées du planning
        crenos = []              # liste des creneaux du planning par poste
        for po in postes:
            crenos.append(po.UUID_poste)
        creneaux = Creneau.objects.filter(poste_id__in=crenos)       # creneaux des postes du planning
        try :
            for v in creneaux:
                # print('###### creneaux : {}'.format(v.nom))
                data["Creneaux"] = creneaux.order_by('debut')  # creneaux des postes du planning
        except :
            print('###### pas de creneaux sur ce planning')

    if uuid_poste:  # selection d'un poste
        poste = Poste.objects.get(UUID_poste=uuid_poste)
        creneaux = Creneau.objects.filter(poste_id=uuid_poste)
        data["Poste"] = poste  # recupere le poste selectionnée
        data["Creneaux"] = creneaux.order_by('debut')  # recupere les creneaux du poste
    return render(request, "evenement/evenement_detail.html", data)
