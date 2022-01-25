import logging
from sys import api_version

from django.http import HttpResponseRedirect
from association.models import Association

from benevole.models import Personne, ProfileBenevole
from evenement.models import Creneau, Equipe, Evenement
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls.base import reverse
from django.urls import reverse_lazy
from django.views import generic
from django.db.models import Q
from datetime import date

from benevole.forms import BenevoleForm, PersonneForm, RegisterForm
from benevole.models import ProfileAdministrateur, ProfileOrganisateur, ProfileResponsable, ProfileBenevole

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

################################################
#            fonctions 
################################################

def GroupeUtilisateur(request):
    """renvoi le groupe le plus permissif du user connecté """
    if request.user.groups.filter(name = 'Administrateur').exists():
        return 'Administrateur'
    elif request.user.groups.filter(name = 'Organisateur').exists():
        return 'Organisateur'
    elif request.user.groups.filter(name = 'Responsable').exists():
        return 'Responsable'
    elif request.user.groups.filter(name = 'Benevole').exists():
        return 'Benevole'

def RoleUtilisateur(request, **kwargs): # remplace GroupeUtilisateur pour avoir le role par evenement
    """
        renvoi les roles du user connecte 
        filtre si en parametre est passé 
        ass : pour l'asso uniquement
        ev : pour l'evenement uniquement
        eq : pour l'equipe uniquement
        plan : pour le planning uniquement

        sortie
        dictionnaire: groupe, queryset
     """
    groupes_liste = ['Administrateur', 'Organisateur', 'Responsable', 'Benevole']
    association, evenement, equipe, planning = "", "" , "", ""
    out={}
    if kwargs.get('plan'):
        # roles de la personne dans le planning
        planning = kwargs.get('plan')
        equipe = Equipe.objects.get(UUID=planning.equipe_id)
        evenement = Evenement.objects.get(UUID=planning.evenement_id)
        association = Association.objects.get(UUID=evenement.association_id)
        try:
            out['Administrateur'] = Association.objects.filter( \
                                    Q(administrateur=ProfileAdministrateur.objects.get(personne=request.user)), \
                                    Q(UUID=association.UUID))
        except:
            out['Administrateur'] = ""
        try:
            out['Organisateur'] = Evenement.objects.filter( \
                                    Q(organisateur=ProfileOrganisateur.objects.get(personne_id=request.user.UUID)), \
                                    Q(UUID=evenement.UUID))
        except:
            out['Organisateur'] = ""
        try:
            out['Responsable'] = Equipe.objects.filter( \
                                    Q(responsable=ProfileResponsable.objects.get(personne_id=request.user.UUID)), \
                                    Q(UUID=equipe.UUID))
        except:
            out['Responsable'] = ""
        try:
            out['Benevole'] = Creneau.objects.filter( \
                                    Q(benevole=ProfileBenevole.objects.get(personne_id=request.user.UUID)), \
                                    Q(planning_id=planning.UUID))
        except:
            out['Benevole'] = ""

    if kwargs.get('eq'):
        # roles de la personne dans l equipe
        equipe = kwargs.get('eq')
        evenement = Evenement.objects.get(UUID=equipe.evenement_id)
        association = Association.objects.get(UUID=evenement.association_id)
        try:
            out['Administrateur'] = Association.objects.filter( \
                                    Q(administrateur=ProfileAdministrateur.objects.get(personne=request.user)), \
                                    Q(UUID=association.UUID))
        except:
            out['Administrateur'] = ""
        try:    
            out['Organisateur'] = Evenement.objects.filter( \
                                    Q(organisateur=ProfileOrganisateur.objects.get(personne_id=request.user.UUID)), \
                                    Q(UUID=evenement.UUID))
        except:
            out['Organisateur'] = ""
        try:    
            out['Responsable'] = Equipe.objects.filter( \
                                    Q(responsable=ProfileResponsable.objects.get(personne_id=request.user.UUID)), \
                                    Q(UUID=equipe.UUID))
        except:
            out['Responsable'] = ""
        try:    
            out['Benevole'] = Creneau.objects.filter( \
                                    Q(benevole=ProfileBenevole.objects.get(personne_id=request.user.UUID)), \
                                    Q(equipe=equipe))
        except:
            out['Benevole'] = ""

    if kwargs.get('ev'):
        # roles de la personne dans l evenement
        evenement = kwargs.get('ev')
        association = Association.objects.get(UUID=evenement.association_id)
        try:
            out['Administrateur'] = Association.objects.filter( \
                                    Q(administrateur=ProfileAdministrateur.objects.get(personne=request.user)), \
                                    Q(UUID=association.UUID))
        except:
            out['Administrateur'] = ""
        try:
            out['Organisateur'] = Evenement.objects.filter( \
                                    Q(organisateur=ProfileOrganisateur.objects.get(personne_id=request.user.UUID)), \
                                    Q(UUID=evenement.UUID))
        except:
            out['Organisateur'] = ""
        try:
            out['Responsable'] =  Equipe.objects.filter( \
                                    Q(responsable=ProfileResponsable.objects.get(personne_id=request.user.UUID)), \
                                    Q(evenement=evenement))
        except:
            out['Responsable'] = ""
        try:
            out['Benevole'] = Creneau.objects.filter( \
                                    Q(benevole=ProfileBenevole.objects.get(personne_id=request.user.UUID)), \
                                    Q(evenement=evenement))
        except:
            out['Benevole'] = ""
    if kwargs.get('ass'):
        # roles de la personne dans l asso
        association = kwargs.get('ass')
        try:
            out['Administrateur'] = Association.objects.filter( \
                                    Q(administrateur=ProfileAdministrateur.objects.get(personne=request.user)), \
                                    Q(UUID=association.UUID))
        except:
            out['Administrateur'] = ""
        try:
            out['Organisateur'] = Evenement.objects.filter( \
                                    Q(organisateur=ProfileOrganisateur.objects.get(personne_id=request.user.UUID)), \
                                    Q(association_id=association.UUID))
        except:
            out['Organisateur'] = ""
        try:
            out['Responsable'] = Equipe.objects.filter( \
                                    Q(responsable=ProfileResponsable.objects.get(personne_id=request.user.UUID)), \
                                    Q(evenement__association=association))
        except:
            out['Responsable'] = ""
        try:    
            out['Benevole'] = Creneau.objects.filter( \
                                    Q(benevole=ProfileBenevole.objects.get(personne_id=request.user.UUID)), \
                                    Q(evenement__association=association))
        except:
            out['Benevole'] = ""

    if not planning and not equipe and not evenement and not association:
        # roles de la personne sur tout le logiciel
        try:    
            out['Administrateur'] = Association.objects.filter( \
                                    Q(administrateur=ProfileAdministrateur.objects.get(personne=request.user)))
        except:
            out['Administrateur'] = ""
        try:    
            out['Organisateur'] = Evenement.objects.filter( \
                                    Q(organisateur=ProfileOrganisateur.objects.get(personne_id=request.user.UUID)))
        except:
            out['Organisateur'] = ""
        try:    
            out['Responsable'] = Equipe.objects.filter( \
                                    Q(responsable=ProfileResponsable.objects.get(personne_id=request.user.UUID)))
        except:
            out['Responsable'] = ""
        try:    
            out['Benevole'] = Creneau.objects.filter( \
                                    Q(benevole=ProfileBenevole.objects.get(personne_id=request.user.UUID)))      
        except:
            out['Benevole'] = ""

    return out


################################################
#            views 
################################################

# nouvelle class d'enregistrement 
class InscriptionView(generic.CreateView):
    form_class = RegisterForm               # on utilise notre form custom
    success_url = reverse_lazy('login')
    template_name = 'benevole/inscription.html'

@login_required(login_url='login')
def Home(request):
    """
        page profile de login et principale du benevole
    """
    # log les donnees post
    print('#########################################################')
    for key, value in request.POST.items():
        print('#        POST -> {0} : {1}'.format(key, value))
    print('#########################################################')
    data = {
        "FormPersonne" : PersonneForm(),  # form personne non liée
        "Evenements" : Evenement.objects.all().order_by("debut"),  # liste de tous les evenements
        "Evenements_inscrit" : Evenement.objects.filter(Q(debut__gt=date.today()),Q(benevole__personne_id=request.user.UUID)).order_by("debut"), # evenements à venir où le benevole est deja inscrit
        "Evenements_disponible" : Evenement.objects.filter(Q(debut__gt=date.today()),
                                                           ~Q(benevole__personne_id=request.user.UUID),
                                                           Q(inscription_debut__lte=date.today()), 
                                                           Q(inscription_fin__gt=date.today())).order_by("debut"),# evenements à venir , benevole pas inscrit , inscription ouvertes

        "Assos": Association.objects.all() # liste toutes les assosciations pour admin, a filtrer par assos affectées a administrateur
    }
    # récupère dans la session l'uuid de l'association, si on est passé par l'asso
    try:
        uuid_evenement = request.session['uuid_evenement']
        print('evenement : {}'.format(uuid_evenement))
        evenement = Evenement.objects.get(UUID=uuid_evenement)
        #data["Evenement"] = evenement
        data["Benevoles"] = ProfileBenevole.objects.filter(BenevolesEvenement=evenement)  # objets benevoles de l'evenement
    except:
        print('pas passé la page evenement')

    # ajouter un tableau des evenements avec : pas encore ouvert / ouvert / inscriptions closes /en cours /fini / benevole inscrit
    # pour trier dans le home du benevoles les evenements et le fait qu'il puisse s'y inscrire

    if request.method == 'POST':
        if 'inscription_event' in request.POST:
            # on ajoute le bénévole à l evenement
            insc_ev = Evenement.objects.get(UUID=request.POST.get('inscription_event'))
            insc_be = ProfileBenevole.objects.get(personne_id=request.user.UUID)
            if insc_be and insc_ev:
                logger.info('bénévole {} inscrit à l\'evenement {}'.format(insc_be, insc_ev))
                insc_ev.benevole.add(insc_be)
                # redirige vers la page evenement
                return HttpResponseRedirect('evenement/{}'.format(insc_ev.UUID))

    # on redirige vers la page profile tant que celui-ci n est pas rempli
    if request.user.is_authenticated :
        if not request.user.last_name:
            return Profile(request)

    return render(request, "benevole/home.html", data)


@login_required(login_url='login')
def Profile(request):
    """
        page profile des personnes
    """
    # log les donnees post
    print('#########################################################')
    for key, value in request.POST.items():
        print('#        POST -> {0} : {1}'.format(key, value))
    print('#########################################################')

    # un bénévole accede a son profile
    if request.method == "POST" and request.POST.get('personne'):
        # si on a de donnes post, on sauvegarde les formulaires
        FormPersonne = PersonneForm(request.POST, instance=Personne.objects.get(UUID=request.POST.get('personne')))
        try:
            # on a un profile bénévole déjà cree, on le recupere
            FormBenevole = BenevoleForm(request.POST, instance=ProfileBenevole.objects.get(personne_id=request.POST.get('personne')))
        except:
            # nouveau profile benevole
            FormBenevole = BenevoleForm(request.POST,
                                        #personne_id=request.POST.get('personne'),
                                        #assopartenaire_id=request.POST.get('assopartenaire'),
                                        #message=request.POST.get('message'), 
                                        )
            logger.info('nouveau bénévole inscrit: {0} {1} - {2}'.format(request.POST.get('last_name'), request.POST.get('first_name'), request.user.email))

        if FormPersonne.is_valid() and FormBenevole.is_valid():
            FormPersonne.save()   
            FormBenevole.save(Personne.objects.get(UUID=request.POST.get('personne')))
            # cree le lien evenement - benevole : a changer ici on est sur un seul evenement, il faudra voir comment s'inscrire a un evenement parmis d'autres
            evenement = Evenement.objects.filter().first()
            plop = ProfileBenevole.objects.get(UUID=request.user.profilebenevole.UUID)
            # ajoute notre benevole dans le champs manytomany 
            evenement.benevole.add(ProfileBenevole.objects.get(UUID=plop.UUID)) 
            # on redirige vers la page evenements si les forms sont remplies
            return redirect("home")
            
    try : 
        profile_benevole = BenevoleForm(instance=ProfileBenevole.objects.get(personne_id=request.user.UUID))  # form benevole liée
    except :
        # sinon initial, on va lier le profile à l evenement
        # profile_benevole = BenevoleForm(initial={'evenement' : [i.id for i in Evenement_inst.evenement.all()]})
        profile_benevole = BenevoleForm()
    # on construit nos objets a passer au template dans le dictionnaire data
    data = {
        "FormPersonne" : PersonneForm(instance=Personne.objects.get(UUID=request.user.UUID)),  # form personne liée
        "FormBenevole" : profile_benevole, # form benevole liée
        "Evenements" : "",  # liste de tous les evenements
        "Action" : "modifier",
    }
    return render(request, "benevole/profile.html", data)