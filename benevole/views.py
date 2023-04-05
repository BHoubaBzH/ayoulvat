import logging
from sys import api_version

from django.http import HttpResponseRedirect
from association.models import AssoPartenaire, Association
from ayoulvat.methods import envoi_courriel
from ayoulvat.languages import *

from benevole.models import Personne, ProfileBenevole
from evenement.models import Creneau, Equipe, Evenement, evenement_benevole_assopart
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls.base import reverse
from django.urls import reverse_lazy
from django.views import generic
from django.db.models import Q
from datetime import date

from benevole.forms import BenevoleForm, PersonneForm, RegisterForm
from benevole.models import ProfileAdministrateur, ProfileOrganisateur, ProfileResponsable, ProfileBenevole
from django.contrib import messages

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

################################################
#            fonctions 
################################################

def RoleUtilisateur(request, objet="", filtre=""): # remplace GroupeUtilisateur pour avoir le role par evenement
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
    association, evenement, equipe, planning = "", "" , "", ""
    out={}
    if objet=='plan':
        # roles de la personne dans le planning
        planning = filtre
        equipe = Equipe.objects.get(UUID=planning.equipe_id)
        evenement = Evenement.objects.get(UUID=planning.evenement_id)
        association = Association.objects.get(UUID=evenement.association_id)
        filtre_asso = 'Q(administrateur=ProfileAdministrateur.objects.get(personne_id="{}")), Q(UUID="{}")'.format(request.user.UUID, association.UUID)
        filtre_ev = 'Q(organisateur=ProfileOrganisateur.objects.get(personne_id="{}")), Q(UUID="{}")'.format(request.user.UUID, evenement.UUID)
        filtre_eq = 'Q(responsable=ProfileResponsable.objects.get(personne_id="{}")), Q(UUID="{}")'.format(request.user.UUID, equipe.UUID)
        #filtre_cre = 'Q(benevole=ProfileBenevole.objects.get(personne_id="{}")), Q(planning_id="{}")'.format(request.user.UUID, planning.UUID)
    if objet=='eq':
        # roles de la personne dans l equipe
        equipe = filtre
        evenement = Evenement.objects.get(UUID=equipe.evenement_id)
        association = Association.objects.get(UUID=evenement.association_id)
        filtre_asso = 'Q(administrateur=ProfileAdministrateur.objects.get(personne_id="{}")), Q(UUID="{}")'.format(request.user.UUID, association.UUID)
        filtre_ev = 'Q(organisateur=ProfileOrganisateur.objects.get(personne_id="{}")), Q(UUID="{}")'.format(request.user.UUID, evenement.UUID)
        filtre_eq = 'Q(responsable=ProfileResponsable.objects.get(personne_id="{}")), Q(UUID="{}")'.format(request.user.UUID, equipe.UUID)
        #filtre_cre = 'Q(benevole=ProfileBenevole.objects.get(personne_id="{}")), Q(equipe_id="{}")'.format(request.user.UUID, equipe.UUID)
    if objet=='ev':
        # roles de la personne dans l evenement
        evenement = filtre
        association = Association.objects.get(UUID=evenement.association_id)
        filtre_asso='Q(administrateur=ProfileAdministrateur.objects.get(personne_id="{}")), Q(UUID="{}")'.format(request.user.UUID, association.UUID)
        filtre_ev = 'Q(organisateur=ProfileOrganisateur.objects.get(personne_id="{}")), Q(UUID="{}")'.format(request.user.UUID, evenement.UUID)
        filtre_eq = 'Q(responsable=ProfileResponsable.objects.get(personne_id="{}")), Q(evenement_id="{}")'.format(request.user.UUID, evenement.UUID)
        #filtre_cre = 'Q(benevole=ProfileBenevole.objects.get(personne_id="{}")), Q(evenement_id="{}")'.format(request.user.UUID, evenement.UUID)
    if objet=='ass':
        # roles de la personne dans l asso
        association = filtre
        filtre_asso = 'Q(administrateur=ProfileAdministrateur.objects.get(personne_id="{}")), Q(UUID="{}")'.format(request.user.UUID, association.UUID)
        filtre_ev = 'Q(organisateur=ProfileOrganisateur.objects.get(personne_id="{}")), Q(association_id="{}")'.format(request.user.UUID, association.UUID)
        filtre_eq = 'Q(responsable=ProfileResponsable.objects.get(personne_id="{}")), Q(evenement__association_id="{}")'.format(request.user.UUID, association.UUID)
        #filtre_cre = 'Q(benevole=ProfileBenevole.objects.get(personne_id="{}")), Q(evenement__association_id="{}")'.format(request.user.UUID, association.UUID)
        filtre_ben = 'Q(benevole="{}"), Q(evenement__association_id="{}")'.format(request.user.profilebenevole, association.UUID)
    if not planning and not equipe and not evenement and not association:
        # roles de la personne sur tout le logiciel
        filtre_asso = 'Q(administrateur=ProfileAdministrateur.objects.get(personne_id="{}"))'.format(request.user.UUID)
        filtre_ev = 'Q(organisateur=ProfileOrganisateur.objects.get(personne_id="{}"))'.format(request.user.UUID)
        filtre_eq = 'Q(responsable=ProfileResponsable.objects.get(personne_id="{}"))'.format(request.user.UUID)
        #filtre_cre = 'Q(benevole=ProfileBenevole.objects.get(personne_id="{}"))'.format(request.user.UUID)
 
    try:
        out['Administrateur'] = eval('Association.objects.filter({})'.format(filtre_asso))
    except:
        out['Administrateur'] = ""
    try:
        out['Organisateur'] = eval('Evenement.objects.filter({})'.format(filtre_ev))
    except:
        out['Organisateur'] = ""
    try:
        out['Responsable'] = eval('Equipe.objects.filter({})'.format(filtre_eq))
    except:
        out['Responsable'] = ""
    try:
        out['Benevole'] = Evenement.objects.filter(Q(benevole=request.user.profilebenevole), Q(UUID=evenement.UUID))
    except:
        out['Benevole'] = ""
    return out

def ListeGroupesUserFiltree(request, objet="", filtre=""):
    """
        roles du user connecte
        filtre si en parametre est passé 
        objet :
            ass : pour l'asso uniquement
            ev : pour l'evenement uniquement
            eq : pour l'equipe uniquement
            plan : pour le planning uniquement
        filtre : objet bdd 

        sortie
            liste: groupes aux quel le user appartient en fonction du filtre
    """
    # groupes du logiciel
    # groupes_liste=Group.objects.all()
    RolesUtilisateur = []
    for role, entite in RoleUtilisateur(request, objet, filtre).items():
        if entite:
            logger.info(f'#        {role:<15} ->')
            for obj in entite:
                logger.info(f'#                               {obj.nom:<25}   {obj.UUID}')
                RolesUtilisateur.append(role)
    return RolesUtilisateur
 
def check_majeur(date_naissance, date_evenement):
    '''
        vérifie si le bénévole est majeur ou non au debut de l'evenement
        entree : date de naissance du bénévole , date de début de l'evenement
        sortie : booleen , True : Majeur , False : Mineur
    '''
    pivot = 6570 # age pivot : 18 ans = 6570 jours
    delta = date_evenement - date_naissance
    if delta.days < pivot:
        return False # mineur
    else:
        return True # majeur

def devenir_benevole(user, **kwargs):
    # on ajoute le bénévole à l evenement
    if 'POST' in kwargs:
        # un benevole s inscrit a l evenement sur la page des evenements
        post = kwargs.get('POST')
        insc_ev = Evenement.objects.get(UUID=post.get('inscription_event'))
    elif 'EVENEMENT' :
        # un admin/orga decide de devenir benevole sur l evenement
        evt = kwargs.get('EVENEMENT')
        insc_ev = evt
    insc_be = ProfileBenevole.objects.get(personne_id=user.UUID)
    if insc_ev:
        logger.info('bénévole {} inscrit à l\'evenement {}'.format(insc_be, insc_ev))
        insc_ev.benevole.add(insc_be)

def envoi_courriel_orga_inscription(request):
    """
        envoi un courrier quand un bénévole s inscrit a l evenement
    """
    evt_uuid = request.POST.get('inscription_event')
    evt = Evenement.objects.get(UUID=evt_uuid)
    emails_orga = []
    logger.debug(f'evt nom : {evt.nom}')
    logger.debug(f'ben nom : {request.user}')
    for orga in evt.organisateur.all():
        emails_orga.append(orga.personne.email)
    if emails_orga:
        sujet = '[Ayoulvat] Nouveau bénévole inscrit à ton évènement'
        message_text = '{} vient de s\'inscrit à l\'évènement {} comme bénévole'.format(request.user, evt)
        message_html = ' \
            <html> <head> </head> <body> {} vient de s\'inscrit à l\'évènement {} comme bénévole</body> </html> \
            '.format(request.user, evt)
        from_courriel = 'no-reply@deusta.bzh'
        to_courriel = emails_orga
        logger.debug(to_courriel)
        if sujet and to_courriel and from_courriel:
            envoi_courriel(sujet, message_text, from_courriel, to_courriel, message_html)

################################################
#            views 
################################################

# nouvelle class d'enregistrement 
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
    # log les donnees post
    logger.info('#########################################################')
    for key, value in request.POST.items():
        logger.info(f'#        POST -> {key} : {value}')
    logger.info('#########################################################')
    data = {
        "FormPersonne" : PersonneForm(),  # form personne non liée
        #"Evenements" : Evenement.objects.all().order_by("debut"),  # liste de tous les evenements
        # evenements a venir ou en cours où le benevole est deja inscrit 
        "Evenements_inscrit" : Evenement.objects.filter(
                                        Q(fin__gt=date.today()),
                                        Q(benevole__personne_id=request.user.UUID)).order_by("debut"), 
        "Evenements_disponible" : Evenement.objects.filter(
                                        Q(fin__gt=date.today()),
                                        ~Q(benevole__personne_id=request.user.UUID)).order_by("debut"),# evenements à venir , ou en cours benevole pas inscrit 
        #"Assos": Association.objects.all(),
        # attention ok car on ne peut estre admin que d un evenement
        "Assos" : [request.user.profileadministrateur.association],
        "Text": text_template[language], # textes traduits
    }
    # check si on a un administrateur:
    logger.info('#########################################################')
    logger.info('#   utilisateur connecté: ')
    logger.info(f'#        {request.user.first_name} {request.user.last_name} ')
    logger.info('#   roles : ')

    RolesUtilisateur = ListeGroupesUserFiltree(request)
    try:
        if 'Administrateur' in RolesUtilisateur:
            data['Administrateur'] = "oui" # passe les roles 
    except:
        logger.error('erreur dans les RolesUtilisateur')
    logger.info('#########################################################')  

    try:
        data["Ev_ass_par_benevole"] = evenement_benevole_assopart.objects.filter(
                                        Q(profilebenevole=request.user.profilebenevole)) # contient la queryset de la table relationnelle evenement, benevole, asso part filtrée sur le bénévole connecté
    except:
        print('pas encore de profile benevole -> page de profile')
    # récupère dans la session l'uuid de l'association, si on est passé par l'asso
    try:
        uuid_evenement = request.session['uuid_evenement']
        evenement = Evenement.objects.get(UUID=uuid_evenement)
        #data["Evenement"] = evenement
        #data["Benevoles"] = ProfileBenevole.objects.filter(BenevolesEvenement=evenement)  # objets benevoles de l'evenement
    except:
        # pas passé la page evenement
        pass
    # pour trier dans le home du benevoles les evenements et le fait qu'il puisse s'y inscrire
    if request.method == 'POST' and ProfileBenevole.objects.filter(personne_id=request.user.UUID).exists(): #post et le user a renseigné son profile
        if 'inscription_event' in request.POST:
            try:
                devenir_benevole(request.user, POST=request.POST)
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
    logger.info('#########################################################')
    for key, value in request.POST.items():
        logger.info(f'#        POST -> {key} : {value}')
    logger.info('#########################################################')

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