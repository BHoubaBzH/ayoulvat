from django.contrib.auth.decorators import login_required
from django.shortcuts import render

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
def detail_evenement(request, uuid_event):
    """
    détails d'un evenement
    """
    # store dans la session le uuid de l'evenement
    request.session['uuid_evenement'] = uuid_event

    evenement = Evenement.objects.get(UUID_evenement=uuid_event)
    equipes = Equipe.objects.filter(evenement_id=uuid_event)
    data = {

        "Evenement": evenement,
        "Equipes": equipes,
    }
    return render(request, "evenement/evenement_detail.html", data)


################################################
##      views equipes
################################################
@login_required(login_url='login')
def liste_equipes(request):
    """
    liste des équipes
    """
    # récupère dans la session l'uuid de l'association
    uuid_evt = request.session.get('uuid_evenement')

    data = {
        # on filtre les équipes sur celles de l'evenement uniquement
        "Equipes": Equipe.objects.filter(evenement_id=uuid_evt),
    }
    return render(request, 'evenement/equipes_liste.html', data)


@login_required(login_url='login')
def detail_equipe(request, uuid_equipe):
    """
    détails d'une équipe
    """
    # store dans la session le uuid de l'equipe
    request.session['uuid_equipe'] = uuid_equipe

    equipe = Equipe.objects.get(UUID_equipe=uuid_equipe)
    plannings = Planning.objects.filter(equipe_id=uuid_equipe)
    data = {
        "Equipe": equipe,
        "Plannings" : plannings,
    }
    return render(request, 'evenement/equipe_detail.html', data)


################################################
##      views plannings
################################################
@login_required(login_url='login')
def liste_plannings(request):
    """
    liste des plannings
    """
    # récupère dans la session l'uuid de l'equipe
    uuid_equipe = request.session.get('uuid_equipe')

    data = {
        # on filtre les plannings sur ceux de l'equipe uniquement
        "Plannings": Planning.objects.filter(equipe_id=uuid_equipe),
    }
    return render(request, 'evenement/plannings_liste.html', data)


@login_required(login_url='login')
def detail_planning(request, uuid_planning):
    """
    détails d'un planning
    """
    # store dans la session le uuid du planning
    request.session['uuid_planning'] = uuid_planning

    planning = Planning.objects.get(UUID_planning=uuid_planning)
    postes = Poste.objects.filter(planning_id=uuid_planning)
    data = {
        "Planning": planning,
        "Postes": postes,
    }
    return render(request, 'evenement/planning_detail.html', data)


################################################
##      views postes
################################################
@login_required(login_url='login')
def liste_postes(request):
    """
    liste des postes
    """
    # récupère dans la session l'uuid du planning
    uuid_plan = request.session.get('uuid_planning')

    data = {
        # on filtre les postes sur ceux des plannings uniquement
        "Postes": Poste.objects.filter(planning_id=uuid_plan),
    }
    return render(request, 'evenement/postes_liste.html', data)


@login_required(login_url='login')
def detail_poste(request, uuid_poste):
    """
    détails d'un poste
    """
    # store dans la session le uuid du poste
    request.session['uuid_poste'] = uuid_poste

    poste = Poste.objects.get(UUID_poste=uuid_poste)
    creneaux = Creneau.objects.filter(poste_id=uuid_poste).order_by('debut')
    data = {
        "Poste": poste,
        "Creneaux": creneaux, # pb sur NoReverseMatch
    }
    return render(request, 'evenement/poste_detail.html', data)


################################################
##      views céneaux
################################################
@login_required(login_url='login')
def liste_creneaux(request):
    """
    liste des creneaux
    """
    # récupère dans la session l'uuid du poste
    uuid_poste = request.session.get('uuid_poste')

    data = {
        # on filtre les postes sur ceux des plannings uniquement
        "Creneaux": Creneau.objects.filter(poste_id=uuid_poste),
    }
    return render(request, 'evenement/creneaux_liste.html', data)


@login_required(login_url='login')
def detail_creneau(request, uuid_creneau):
    """
    détails d'un planning
    """
    # store dans la session le uuid du creneau
    request.session['uuid_creneau'] = uuid_creneau

    creneau = Creneau.objects.get(UUID_creneau=uuid_creneau)
    data = {
        "Creneau": creneau,
    }
    return render(request, 'evenement/creneau_detail.html', data)
