from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render

from benevole.models import ProfileBenevole, ProfilePersonne
from evenement.models import Evenement, Equipe, Planning, Poste, Creneau


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

    # on construit nos objet avec l'uuid de l'evenement
    evenement = Evenement.objects.get(UUID_evenement=uuid_evenement)
    equipes = Equipe.objects.filter(evenement_id=uuid_evenement)

    data = {
        "Evenement": evenement,
        "Equipes": equipes,
    }

    # recupere les uuid en POST ou en session si ils on été stockés, but est de tout gerer dans une seule page:
    if request.POST.get('uuid_equipe'):
        uuid_equipe = request.POST.get('uuid_equipe')
    elif request.session.get('uuid_equipe'):
        uuid_equipe = request.session.get('uuid_equipe')
    if request.POST.get('uuid_planning'):
        uuid_planning = request.POST.get('uuid_planning')
    elif request.session.get('uuid_planning'):
        uuid_planning = request.session.get('uuid_planning')
    if request.POST.get('uuid_poste'):
        uuid_poste = request.POST.get('uuid_poste')
    elif request.session.get('uuid_poste'):
        uuid_poste = request.session.get('uuid_poste')
        
    if uuid_equipe: # selection d'une équipe
        # store dans la session le uuid de l'equipe
        request.session['uuid_equipe'] = uuid_equipe
        equipe = Equipe.objects.get(UUID_equipe=uuid_equipe)
        plannings = Planning.objects.filter(equipe_id=uuid_equipe).order_by('debut')
        data["Equipe"] = equipe
        data["Plannings"] = plannings
    if uuid_planning:   # selection d'un planning
        # store dans la session le uuid du planning
        request.session['uuid_planning'] = uuid_planning
        planning = Planning.objects.get(UUID_planning=uuid_planning)
        postes = Poste.objects.filter(planning_id=uuid_planning).order_by('nom')
        data["Planning"] = planning
        data["Postes"] = postes
    if uuid_poste:  # selection d'un poste
        # store dans la session le uuid du poste
        request.session['uuid_poste'] = uuid_poste
        poste = Poste.objects.get(UUID_poste=uuid_poste)
        creneaux = Creneau.objects.filter(poste_id=uuid_poste).order_by('debut')
        data["Poste"] = poste
        data["Creneaux"] = creneaux
    return render(request, "evenement/evenement_detail.html", data)
