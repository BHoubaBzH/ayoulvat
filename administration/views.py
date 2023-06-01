from datetime import date, timedelta

from django.http.response import Http404
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views.generic import ListView, View
from django.db.models import Q

from utils.evenement import *
from utils.generic import *
from utils.benevole import *
from utils.administration import *
from ayoulvat.languages import *

from benevole.forms import BenevoleForm, PersonneForm
from benevole.models import ProfileBenevole, ProfileResponsable
from evenement.models import Creneau, Equipe, Evenement, Planning, evenement_benevole_assopart
from ayoulvat.languages import *

from django.shortcuts import render

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

################################################
#            views 
################################################

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(user_passes_test(lambda u: u.groups.filter(name__in=['Administrateur','Organisateur','Responsable']).exists()), name='dispatch')
class CreneauxListView(ListView):
    #queryset = ProfileBenevole.objects.filter(personne__is_active='1')
    template_name = "administration/evenement/creneaux.html"

    def dispatch(self, request, *args, **kwargs):
        self.Evt = Evenement.objects.get(UUID=self.request.session['uuid_evenement']) # recuper l evenement
        self.Asso = self.Evt.association # recuper l asso
        self.queryset = list(self.Evt.creneau_set.all().order_by('debut').select_related('poste', 'planning', 'equipe', 'benevole', 'evenement'))
        self.context = { 
            # nav bar infos : debut
            "EvtOuvertBenevoles" : inscription_ouvert(self.Evt.inscription_debut, self.Evt.inscription_fin), # integer précisant si on est avant/dans/après la période de modification des creneaux
            # nav bar infos : fin
            "Association" : self.Asso,
            "Evenement" : self.Evt, 
            "Creneaux" : self.queryset,
            "Text": text_template[language], # textes traduits 
        }
        logger.info(f'{__class__.__name__} : dispatch')
        return super().dispatch(request, *args, **kwargs)

    # recupere et traite les données post
    def post(self, request, *args, **kwargs):
        logger.info(f'{__class__.__name__} : post')
        log_post(request.POST)

        return render(request, self.template_name, self.context)

    # envoi les datas au template
    def get_context_data(self, **kwargs):
        logger.info(f'{__class__.__name__} : get_context_data')
        return self.context

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(user_passes_test(lambda u: u.groups.filter(name__in=['Administrateur','Organisateur','Responsable']).exists()), name='dispatch')
class BenevolesListView(ListView):
    #model = ProfileBenevole
    # benevoles actif 
    queryset = ProfileBenevole.objects.filter(personne__is_active='1')
    template_name = "administration/evenement/benevoles.html"

    def dispatch(self, request, *args, **kwargs):
        logger.info(f'{__class__.__name__} : dispatch')
        self.Evt = Evenement.objects.get(UUID=self.request.session['uuid_evenement']) # recuper l evenement
        self.Asso = self.Evt.association # recuper l asso
        self.ListeBenevoles = self.queryset.select_related('personne').filter(BenevolesEvenement=self.Evt).order_by('personne__last_name')  # objets benevoles de l'evenement
        # self.ListeNotBenevoles = self.queryset.select_related('personne').filter(~Q(BenevolesEvenement=self.Evt)).order_by('personne__last_name')  # objets personne non inscrites à l'evenement
        # definit les infos a envoyer au tempate

        self.context = { 
            # nav bar infos : debut
            "EvtOuvertBenevoles"    : inscription_ouvert(self.Evt.inscription_debut, self.Evt.inscription_fin), # integer précisant si on est avant/dans/après la période de modification des creneaux
            # nav bar infos : fin
            "Association"           : self.Asso,
            "Evenement"             : self.Evt, 
            "FormPersonne"          : PersonneForm(), # sert a creer un benevole
            "FormBenevole"          : BenevoleForm(), # sert a creer un benevole

            "Equipes"               : list(Equipe.objects.filter(evenement=self.Evt).order_by('nom')),

            "BenevolesAgeCreneauxAssopart": liste_benevoles_age_creneaux_assopart(self.Evt, self.ListeBenevoles),
            #"NotBenevolesAgeCreneauxAssopart": liste_benevoles_age_creneaux_assopart(self.Evt, self.ListeNotBenevoles),
            "EvtBeneAssopar"        : list(self.Evt.evenement_benevole_assopart_set.all()),

            "Administrateurs"       : list(self.Asso.administrateur.all()),
            "Organisateurs"         : list(self.Evt.organisateur.all().select_related('personne')),
            "Responsables"          : list(ProfileResponsable.objects.select_related('personne').filter(ResponsableEquipe__in=self.Evt.equipe_set.all())),

            "Text"                  : text_template[language], # textes traduits 

            "Emails_benevoles_par_planning" : emails_benevoles_par_planning(self.Evt),
            "Emails_benevoles_par_equipe"   : emails_benevoles_par_equipe(self.Evt),
            "Emails_benevoles_evenement"    : emails_benevoles_evenement(self.Evt),
            "Emails_benevoles_sans_creneaux": emails_benevoles_sans_creneaux(self.Evt),
            "Emails_benevoles_un_creneau"   : emails_benevoles_un_creneau(self.Evt),
            "Emails_responsables"           : emails_responsables(self.Evt),
        }

        return super().dispatch(request, *args, **kwargs)

    # recupere et traite les données post
    def post(self, request, *args, **kwargs):
        logger.info(f'{__class__.__name__} : post')
        log_post(request.POST)

        # creer un benevole
        if 'benevole_creer' in request.POST:
            formpersonne = PersonneForm(request.POST) 
            formbenevole = BenevoleForm(request.POST)
            if all((formpersonne.is_valid(), formbenevole.is_valid())):
                personneObj = formpersonne.save()
                benevoleObj = formbenevole.save(personneObj)
                # lien entre l evenement et le profilebenevole
                evenementObj = get_object_or_404(Evenement, UUID=request.session['uuid_evenement'])
                evenementObj.benevole.add(benevoleObj)
                #return render(request, self.template_name, self.context )
            else:
                logger.info(f'erreur de creation de bénévole : {formpersonne.errors}')
                raise Http404(f'erreur de creation de bénévole : {formpersonne.errors}')
            ### ajouter la possibilité de lier à un benevole existant deja
            ###             creer lien evenement-profilebenevole
            ### ajouter la possibilite de lier à une personne dans profilebenevole
            ###             creer profilebenevole + line evenement-profilebenevole 

        # lier un benevole à l evenement
        if 'benevole_lier' in request.POST:
            benevole = ProfileBenevole.objects.get(UUID=request.POST.get('benevole_lier'))
            # lie evenement et profilebenevole
            self.Evt.benevole.add(benevole)

        # supprime un benevole de l evenement
        if all(k in request.POST for k in ('benevole_supprimer', 'BenevoleUUID')):   
            # supprime le lien evenement benevole = desinscrit le benevole de l evenement
            benev=ProfileBenevole.objects.get(UUID=request.POST.get('BenevoleUUID'))
            self.Evt.benevole.remove(benev)
            # supprimer les liens des creneaux affecté vers le bénévole
            cren=Creneau.objects.filter(benevole=benev,evenement=self.Evt)
            for cre in cren:
                setattr(cre, 'benevole_id', '')
                cre.save()
        # recharge les listes infos pour mettre à jour suite aux modifs ( creation ou suppression de benevole)
        self.context['Benevoles']=self.queryset.select_related('personne').filter(BenevolesEvenement=self.Evt).order_by('personne__last_name')
        self.context['BenevolesAgeCreneauxAssopart']= liste_benevoles_age_creneaux_assopart(self.Evt, self.context['Benevoles'])
        self.context['NotBenevoles']=self.queryset.select_related('personne').filter(~Q(BenevolesEvenement=self.Evt)).order_by('personne__last_name')
        self.context['NotBenevolesAgeCreneauxAssopart']= liste_benevoles_age_creneaux_assopart(self.Evt, self.context['NotBenevoles'])
            
        # editer un benevole
        #personnesup = get_object_or_404(Personne, UUID=request.POST.get('BenevoleUUID'))
        #if all(k in request.POST for k in ('benevole_editer', 'BenevoleUUID')):
        #    logger.info('benevole édité : {0} {1}'.format(personnesup.last_name, personnesup.first_name))
 
        return render(request, self.template_name, self.context)

    # envoi les datas au template
    def get_context_data(self, **kwargs):
        logger.info(f'{__class__.__name__} : get_context_data')
        return self.context


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(user_passes_test(lambda u: u.groups.filter(name__in=['Administrateur','Organisateur','Responsable']).exists()), name='dispatch')
class DashboardView(View):
    template_name = "administration/evenement/dashboard.html"
 
    def dispatch(self, request, *args, **kwargs):
        logger.info(f'{__class__.__name__} : dispatch')
        
        self.Evt = Evenement.objects.get(UUID=self.request.session['uuid_evenement']) # recuper l evenement
        self.Asso = self.Evt.association # recuper l asso
        self.queryset_c = self.Evt.creneau_set.filter(type="creneau") # les creneau de l evenement
        self.context = {
            # nav bar infos : debut
            "EvtOuvertBenevoles"    : inscription_ouvert(self.Evt.inscription_debut, self.Evt.inscription_fin), # integer précisant si on est avant/dans/après la période de modification des creneaux
            # nav bar infos : fin
            "Association"           : self.Asso,
            "Evenement"             : self.Evt, 
            "Plannings"             : Planning.objects.filter(evenement=self.Evt).order_by('debut'),  # objets planning de l'evenement

            "Creneaux"              : self.queryset_c,
            "Creneaux_libres"       : self.Evt.creneau_set.filter(type="creneau", benevole__isnull=True).count,
            "Creneaux_occupes"      : self.Evt.creneau_set.filter(type="creneau", benevole__isnull=False).count,
            "Assos_partenaires"     : self.Evt.assopartenaire.all(), # partenaire de l evenement
            "Benevoles_par_asso"    : nb_benevoles_par_asso(self.Evt.assopartenaire.all(), self.Evt),
            "Plannings_occupation"  : plannings_occupation(self.Evt.planning_set.order_by('equipe__nom','debut')),

            "Equipes_occupation"    : equipes_occupation(self.Evt.equipe_set.order_by('nom')),
            "Repartition_par_assos" : repartition_par_assos(self.queryset_c.filter(benevole__isnull=False)),
            "Total_heures_benevoles": f'{total_heures_benevoles(self.queryset_c.filter(benevole__isnull=False)).total_seconds()/3600}',

            "Benevoles"             : ProfileBenevole.objects.filter(BenevolesEvenement=self.Evt),  # objets benevoles inscrits à l'evenement
            "Benevoles_c"           : self.queryset_c.filter(benevole__isnull=False).values('benevole_id').distinct(), # objets benevoles inscrits à l'evenement avec au moins un creneau
            "Administrateurs"       : self.Asso.administrateur.all(),
            "Organisateurs"         : self.Evt.organisateur.all().select_related('personne'),
            "Responsables"          : ProfileResponsable.objects.select_related('personne').filter(ResponsableEquipe__in=self.Evt.equipe_set.all()),
            "Text"                  : text_template[language], # textes traduits
        }
        return super().dispatch(request, *args, **kwargs)

    #  
    def get(self, request, *args, **kwargs):
        logger.info(f'{__class__.__name__} : get_context_data')
        return render(request, self.template_name, self.context)

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(user_passes_test(lambda u: u.groups.filter(name__in=['Administrateur','Organisateur','Responsable']).exists()), name='dispatch')
class OrganizationView(View):
    template_name = "administration/evenement/organization.html"
 
    def dispatch(self, request, *args, **kwargs):
        logger.info(f'{__class__.__name__} : dispatch')

        self.Evt = Evenement.objects.get(UUID=self.request.session['uuid_evenement']) # recuper l evenement
        self.context = {
            # nav bar infos : debut
            "EvtOuvertBenevoles"    : inscription_ouvert(self.Evt.inscription_debut, self.Evt.inscription_fin), # integer précisant si on est avant/dans/après la période de modification des creneaux
            # nav bar infos : fin
            "Evenement"             : self.Evt, 
            "Equipes"               : list(Equipe.objects.filter(evenement=self.Evt).order_by('nom')),
            "Plannings"             : list(Planning.objects.filter(evenement=self.Evt).order_by('debut')),
            "Text"                  : text_template[language], # textes traduits
            "PlanningRange"         : planning_range(self.Evt.debut, self.Evt.fin, 30),
            "DicEquipes"            : dic_forms_equipes(self.Evt),
        }
        # liste les roles de l'utilisateur et les envoi au template
        self.RolesUtilisateur = liste_roles_utilisateur(request, self.Evt)
        for role, value in self.RolesUtilisateur.items():
            if value: self.context[role] = value 
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        logger.info(f'{__class__.__name__} : get_context_data')
        self.context["FormPlanning"] = PlanningForm(initial={'evenement': self.Evt, 'equipe': Equipe.objects.filter(evenement_id=self.Evt.UUID).first()})
        return render(request, self.template_name, self.context)

    # recupere et traite les données post
    def post(self, request, *args, **kwargs):
        logger.info(f'{__class__.__name__} : post')
        log_post(request.POST)
        
        #if 'planning' in request.POST:
        #    self.context["Planning"] = Planning.objects.get(UUID=request.POST.get('planning'))

        # Forms non liées de creation d objets
        self.context["FormEquipe"] = EquipeForm(initial={'evenement': self.Evt})
        self.context["FormPoste"] = PosteForm(initial={'evenement': self.Evt,
                                    'equipe': request.POST.get('equipe'),
                                    'planning': request.POST.get('planning')})
        self.context["FormCreneau"] = CreneauForm(initial={'evenement': self.Evt,
                                        'equipe': request.POST.get('equipe'),
                                        'planning': request.POST.get('planning'),
                                        'id_benevole': ProfileBenevole.UUID},
                                pas_creneau=planning_retourne_pas(request),
                                planning_uuid=request.POST.get('planning'),
                                poste_uuid=request.POST.get('poste'),
                                benevole_uuid=request.POST.get('benevole'),
                                personne_connectee=request.user,
                                personne_connectee_roles=self.RolesUtilisateur,
                                evenement=self.Evt.UUID,
                                type=request.POST.get('type'), )
        # admin change un objet de l'evenement : retour en post de la l info modifier / ajouter / supprimer
        if  any(x in request.POST for x in ['creneau_modifier', 'creneau_ajouter', 'creneau_supprimer']):
            self.context["Form"] = forms_creneau(request, self.RolesUtilisateur)
        if any(x in request.POST for x in ['poste_modifier', 'poste_ajouter','poste_supprimer']):
            self.context["Form"] = forms_poste(request)
        if any(x in request.POST for x in ['planning_modifier', 'planning_ajouter', 'planning_supprimer']):
            self.context["Form"] = forms_planning(request)
        if any(x in request.POST for x in ['equipe_modifier', 'equipe_ajouter', 'equipe_supprimer']):
            self.context["Form"] = forms_equipe(request)

        # un admin a cliqué sur le bouton d edition du planning : on va dans la page d un planning
        if any(item in ['planning_editer', 
                        'poste_ajouter', 'poste_modifier', 'poste_supprimer', 
                        'creneau_ajouter', 'creneau_modifier', 'creneau_supprimer'] for item in request.POST):
            self.context["PlanningEditer"] = "oui"

        # edite un planning / ??? a modifier pour sortir de l'edition du planning
        if request.POST.get('planning'):
            print("plan")
            self.context["Planning"] = request.POST.get('planning')

        # recharge les objets apres modifociation
        self.context["Equipes"]     = list(Equipe.objects.filter(evenement=self.Evt).order_by('nom'))
        self.context["DicEquipes"]  = dic_forms_equipes(self.Evt)
        self.context["Plannings"]   = list(Planning.objects.filter(evenement=self.Evt).order_by('debut'))

        return render(request, self.template_name, self.context)