import logging
from sys import api_version

from django.http import Http404, HttpResponseRedirect
from association.models import AssoPartenaire
from utils.generic import envoi_courriel
from ayoulvat.languages import *

from utils.evenement import *
from utils.generic import *
from utils.benevole import *
from utils.administration import *
from ayoulvat.languages import *

from benevole.models import Personne, ProfileAdministrateur, ProfileOrganisateur, ProfileResponsable, ProfileBenevole
from evenement.models import Evenement, evenement_benevole_assopart
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls.base import reverse
from django.urls import reverse_lazy
from django.views import generic
from django.db.models import Q
from datetime import date, datetime

from benevole.forms import BenevoleForm, PersonneForm, RegisterForm
from evenement.forms import EvenementForm
from benevole.models import ProfileBenevole
from django.contrib import messages

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

################################################
#            views 
################################################

# nouvelle class d'enregistrement de personne
class InscriptionView(generic.CreateView):
    form_class = RegisterForm               # on utilise notre form custom
    success_url = reverse_lazy('login')
    template_name = 'benevole/inscription.html'

    def dispatch(self, request, *args, **kwargs):
        logger.info(f'{__class__.__name__} : dispatch') 
        self.context = {
            "Text": text_template[language], # textes traduits 
            "form": RegisterForm,
        }
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        logger.info(f'{__class__.__name__} : get_context_data')
        return render(request, self.template_name, self.context)

@login_required(login_url='login')
def Home(request):
    """
        page profile de login et principale du benevole
    """
    logger.info(f'\n################## {__name__} #####################\n')
    # log les donnees post
    log_post(request.POST)

    data = {
        "FormPersonne" : PersonneForm(),  # form personne non liée
        # evenements a venir ou en cours où le benevole est deja inscrit 
        "Evenements_inscrit" : Evenement.objects.filter(
                                        Q(fin__gt=date.today()),
                                        Q(benevole__personne_id=request.user.UUID)).order_by("debut"), 
        # evenements à venir , ou en cours benevole pas inscrit 
        "Evenements_disponible" : Evenement.objects.filter(
                                        Q(fin__gt=date.today()),
                                        ~Q(benevole__personne_id=request.user.UUID)).order_by("debut"),
        "Text": text_template[language], # textes traduits
    }

    # check si on a un administrateur:
    logger.info('#########################################################')
    logger.info('#   utilisateur connecté: ')
    logger.info(f'#        {request.user.first_name} {request.user.last_name} ')
    logger.info('#   roles : ')
    RolesUtilisateur = ListeGroupesUserFiltree(request)
    logger.info('#########################################################')  

    try:
        # contient la queryset de la table relationnelle evenement, benevole, asso part filtrée sur le bénévole connecté
        data["Ev_ass_par_benevole"] = evenement_benevole_assopart.objects.filter(
                                        Q(profilebenevole=request.user.profilebenevole)) 
    except:
        logger.info('pas encore de profile benevole -> page de profile')

    # trier dans le home du benevoles les evenements et le fait qu'il puisse s'y inscrire
    if request.method == 'POST' and ProfileBenevole.objects.filter(personne_id=request.user.UUID).exists(): #post et le user a renseigné son profile
        if 'inscription_event' in request.POST:
            try:
                devenir_benevole(request.user, POST=request.POST)
                logger.debug(f'evoi notif')
                envoi_courriel_orga_inscription(request)
                messages.success(request, flash[language]['inscr_event_success'].format(Evenement.objects.get(UUID=request.POST.get('inscription_event'))))
                # redirige vers la page evenement
                # return HttpResponseRedirect('evenement/{}'.format(insc_ev.UUID))
            except:
                messages.error(request, flash[language]['inscr_event_error'].format(Evenement.objects.get(UUID=request.POST.get('inscription_event'))))

        if 'asso_perso_change' in request.POST:
            # modifie l asso partenaire pour la quelle le benevole travail
            ben_ev = Evenement.objects.get(UUID=request.POST.get('evenement'))
            ben_ben = ProfileBenevole.objects.get(personne_id=request.user.UUID)
            if request.POST.get('asso_perso'):
                ben_asso = AssoPartenaire.objects.get(UUID=request.POST.get('asso_perso'))
                if ben_ev:
                    obj = evenement_benevole_assopart.objects.get(Q(evenement=ben_ev),Q(profilebenevole=ben_ben))
                    obj.asso_part=ben_asso
                    obj.save()
            else:
                # pas d asso de choisi
                obj = evenement_benevole_assopart.objects.get(Q(evenement=ben_ev),Q(profilebenevole=ben_ben))
                obj.asso_part=None
                obj.save()
                
            # empeche les renvois multiples d email d inscription aux admins 
            HttpResponseRedirect(request.path_info)
    
    # gestion de la form evenement
    if request.method == 'POST':
        if request.POST.get('evenement') == 'creer':
            logger.info( 'on va creer l evenement')
            formevenement = EvenementForm(request.POST)
            if formevenement.is_valid():
                messages.success(request, flash[language]['event_new_success'])
                logger.info('planning modifié ou ajouté')
                formevenement.save()
            else:
                messages.error(request, flash[language]['event_new_error'])
                logger.info(f'erreur de creation de l\'évènement : {formevenement.errors}')
                # raise Http404(f'erreur de creation de l\'évènement : {formevenement.errors}')
                # tbd : creer controle de form sauvegarde de l objet #
        if request.POST.get('evenement') == 'modifier':
            logger.info( 'on va modifier l evenement')
            # tbd : creer controle de form sauvegarde de l objet #

        # duplicate event
        if request.POST.get('evenement_copy'):
            evt = Evenement.objects.get(UUID=request.POST.get('evenement_copy'))
            if request.POST.get('nom'):
                evt.nom = request.POST.get('nom')
            else:
                evt.nom = "copy - " + evt.nom
            # calcul le décalage en jours
            if  request.POST.get('date'):
                delta= datetime.strptime(request.POST.get('date'), '%Y-%m-%d') - evt.debut 
                #logger.info(f' jours de delta : {delta}')
            else:
                # si rien , l evenement commence aujourd hui
                delta=date.datetime.now() - evt.debut 
            #logger.info(f' jours de delta : {str(delta.days)}')
            duplique_evenement(evt, delta.days, request.POST.dict())
        
    # passe les infos de l administrateur
    if RolesUtilisateur['Administrateur']: 
        data['Administrateur'] = RolesUtilisateur['Administrateur'] 
        data['evts'] = Evenement.objects.filter(association__in= data['Administrateur'])
        data['nb_evts_par_asso'] = nb_evenements_par_asso(data['Administrateur'])
        data['FormEvenement'] = EvenementForm() #Forms non liee pour la creation

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
    logger.info(f'\n################## {__name__} #####################\n')
    # log les donnees post
    log_post(request.POST)

    # un bénévole accede a son profile
    if request.method == "POST" and request.POST.get('personne'):
        # si on a de donnes post, on sauvegarde les formulaires
        FormPersonne = PersonneForm(request.POST, instance=Personne.objects.get(UUID=request.POST.get('personne')))
        try:
            # on a un profile bénévole déjà cree, on le recupere
            FormBenevole = BenevoleForm(request.POST, instance=ProfileBenevole.objects.get(personne_id=request.POST.get('personne')))
            print('plop')
        except:
            # nouveau profile benevole
            FormBenevole = BenevoleForm(request.POST,
                                        #personne_id=request.POST.get('personne'),
                                        #assopartenaire_id=request.POST.get('assopartenaire'),
                                        #message=request.POST.get('message'), 
                                        )
            logger.info('nouveau bénévole inscrit: {0} {1} - {2}'.format(request.POST.get('last_name'), request.POST.get('first_name'), request.user.email))
            print(f'form personne {FormPersonne.is_valid()}')
            print(f'form benevole {FormBenevole.is_valid()}')
        if FormPersonne.is_valid() and FormBenevole.is_valid():
            FormPersonne.save()   
            new_profilebenevole = FormBenevole.save(Personne.objects.get(UUID=request.POST.get('personne')))
            logger.debug(f'profile : {new_profilebenevole}')
            messages.success(request, flash[language]['profile_up_success'])
            if request.GET.get('next'):
                next_url=request.GET.get('next')
                return redirect(next_url)
            else:
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
        "Text": text_template[language], # textes traduits 
        "Action" : "modifier",
    }
    return render(request, "benevole/profil.html", data)

