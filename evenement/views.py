from datetime import timedelta

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404
from django.utils.timesince import timesince
from django.forms import formset_factory

from evenement.forms import PosteForm
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
    print('###### planning : {0} - {1}'.format(debut, fin))
    dates_heures = {}
    while debut <= fin:
        # print('date : {}'.format(debut))
        date = debut.strftime("%Y-%m-%d-%H%M")
        heure = debut.strftime("%H:%M")
        dates_heures[date] = [heure, debut]
        debut += timedelta(minutes=delta)
    return dates_heures


def get_infos_benevole(creneaux):
    """
        entree: tableau de creneaux
        donne des infos sur le benevole pour affichage dans le creneau

        retour : liste de tableaux de dictionnaires des models et une duree Time
        {
        'Creneau': creno,
        'Benevole' : benevole.ProfileBenevole,
        'Personne' : benevole.Personne,
        'Responsable' : benevole.ProfileResponsable,
        'Organisateur' : benevole.ProfileOrganisateur,
        'AssoOrigine' : benevole.AssoOrigine,
        'CreneauDuree' timesince(creneau.debut, creneau.fin):
         }
    """
    infos_benevole = []
    for creno in creneaux:
        if creno.benevole_id:   # il y a un benevole lié au creneau
            benevoleinfo = ProfileBenevole.objects.get(UUID_benevole=creno.benevole_id)
            try:
                personneinfo = Personne.objects.get(UUID_personne=benevoleinfo.personne_id)
            except:
                personneinfo = ''
            try:
                responsableinfo = ProfileResponsable.objects.get(personne_id=personneinfo.UUID_personne)
            except:
                responsableinfo = ''
            try:
                organisateurinfo = ProfileOrganisateur.objects.get(personne_id=personneinfo.UUID_personne)
            except:
                organisateurinfo = ''
            try:
                assoorigineinfo = AssoOrigine.objects.get(UUID_assoorigine=personneinfo.assoorigine_id)
            except:
                assoorigineinfo = ''
            infos_benevole.append({'Creneau': creno,
                                   'Benevole': benevoleinfo,
                                   'Personne': personneinfo,
                                   'Responsable': responsableinfo,
                                   'Organisateur': organisateurinfo,
                                   'AssoOrigine': assoorigineinfo,
                                   'CreneauDuree': timesince(creno.debut, creno.fin),})
        else:                    # pas de benevole associé au creneau
            infos_benevole.append({'Creneau': creno,
                                   'Benevole': '',
                                   'Personne': '',
                                   'Responsable': '',
                                   'Organisateur': '',
                                   'AssoOrigine': '',
                                   'CreneauDuree': timesince(creno.debut, creno.fin),})
    return infos_benevole

def forms_postes(the_plan, request):
    """
        entree:
            le planning contenant les postes
            la requete (contenant les infos POST)
        sortie:
            soit :
                dictionnaire
                key : UUID postes
                val : liste avec
                      forms de postes initialisées
                      objet db lié
            soit :
                rien si form sauvegardée
    """
    # sauvegarde notre form modifée envoyée en POST
    if 'poste_changer' in request.POST:
        # objet basé sur model et pk UUID_poste
        poste1 = Poste.objects.get(UUID_poste=request.POST.get('uuid_poste'))
        # form en lien avec l objet précédent
        formposte = PosteForm(request.POST, instance=poste1)
        if formposte.is_valid():
            formposte.save()
        return
    # sauvegarde de notre nouvelle form envoyée eb POST
    elif 'poste_ajouter' in request.POST:
        formposte = PosteForm(request.POST)
        if formposte.is_valid():
            formposte.save()
            print('poste ajouté')
    # cree dans la page toutes nos from pour les postes du planing
    else:
        dic_postes_init = {} # dictionnaire des forms
        # parcours les postes du planning dans la base
        for poste in Poste.objects.filter(planning_id=the_plan):
            # objet basé sur model et pk UUID_poste
            poste1 = Poste.objects.get(UUID_poste=poste.UUID_poste)
            # form en lien avec l objet précédent
            formposte = PosteForm(instance=poste1)
            dic_postes_init[poste.UUID_poste] = formposte # dictionnaire des forms
            # print (' poste UUID : {1} form : {0}'.format(posteform, poste.UUID_poste))
        return dic_postes_init

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
        # "uuid_evenement": uuid_evenement,
        # "FormPoste": formposte,
    }

    # log les donnees post
    for key, value in request.POST.items():
        print('{0} : {1}'.format(key, value))

    # recupere les uuid en POST, but est de tout gerer dans une seule page
    # et d'afficher les infos en fonction des post recus :
    if request.method == "POST":
        if request.POST.get('uuid_equipe'): # selection d'une équipe
            the_equipe = request.POST.get('uuid_equipe')
            data["uuid_equipe"] = the_equipe
        if request.POST.get('uuid_planning'): # selection d'un planning
            the_planning = request.POST.get('uuid_planning')
            data["uuid_planning"] = the_planning
        if request.POST.get('uuid_poste'): # selection d'un poste
            the_poste = request.POST.get('uuid_poste')
            data["uuid_poste"] = the_poste

        ################
        ### paramètres d'affichage
        ################
        if the_equipe:  # selection d'une équipe
            data["Equipe"] = Equipe.objects.get(UUID_equipe=the_equipe)  # equipe selectionnée
            data["Plannings"] = Planning.objects.filter(equipe_id=the_equipe).order_by('debut')  # plannings de l'equipe
        if the_planning:
            planning = Planning.objects.get(UUID_planning=the_planning)
            data["Planning"] = planning  # planning selectionnée
            postes = Poste.objects.filter(planning_id=the_planning).order_by('nom')
            data["Postes"] = postes  # postes du planning
            # instances de form poste : sauvegarde modifs & liste des postes
            dic_postes = forms_postes(the_planning, request)
            data["DicPostes"] = dic_postes
            data["FormPoste"] = PosteForm() # on envoie la form pour ajout d un nouveau poste
            # données formatées du planning
            data["PlanningRange"] = planning_range(planning.debut, planning.fin, planning.pas)

            crenos = []
            for po in postes:
                crenos.append(po.UUID_poste)        # crenos : liste des creneaux du planning par poste
            creneaux = Creneau.objects.filter(poste_id__in=crenos)       # liste des creneaux des postes du planning
            creneaux_benevoles = get_infos_benevole(creneaux)
            # print('{}'.format(creneaux_benevoles))
            try:
                data["Creneaux_Benevoles"] = creneaux_benevoles
            except:
                print('###### pas de creneaux sur ce planning')

        ################
        ### paramètres de gestion du retour des données POST
        ################
        # une personne ayant le droit evenement.delete_poste supprime un poste, on recoit la valeur uuid_poste en post
        if request.POST.get('poste_a_supprimer'):
            print('poste {} supprimé'.format(Poste.objects.filter(UUID_poste=request.POST.get('poste_a_supprimer'))))
            Poste.objects.filter(UUID_poste=request.POST.get('poste_a_supprimer')).delete()

    '''
    # on se garde la possibilité d'afficher sur une granulometrie par poste en plus de planning  
    if uuid_poste:  # selection d'un poste
        poste = Poste.objects.get(UUID_poste=uuid_poste)
        creneaux = Creneau.objects.filter(poste_id=uuid_poste)
        data["Poste"] = poste  # recupere le poste selectionnée
        data["Creneaux"] = creneaux.order_by('debut')  # recupere les creneaux du poste
    '''
    return render(request, "evenement/evenement.html", data)
