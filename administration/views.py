from datetime import date
import logging
from django.contrib.auth.models import User
from django.http.response import Http404, HttpResponseServerError
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views.generic import ListView, View

from benevole.forms import BenevoleForm, PersonneForm
from evenement.models import Creneau, Equipe, Evenement
#from evenement.views import inscription_ouvert
from benevole.views import GroupeUtilisateur
from benevole.models import Personne, ProfileAdministrateur, ProfileBenevole, ProfileOrganisateur, ProfileResponsable
from association.models import AssoPartenaire, Association

from django.http import JsonResponse
from django.shortcuts import render
from django.core import serializers

################################################
#            fonctions 
################################################
def evenement(request):
    """ retourne l'objet evenement en base de l evenement """
    # si on est arrivé là, l evenement existe forcément, donc pas de test à faire
    uuid = request.session['uuid_evenement'] 
    evenement = Evenement.objects.get(UUID=uuid)
    return evenement

def association(request):
    """ retourne l'objet association en base de l evenement """
    # si on est arrivé là, l evenement existe forcément, donc pas de test à faire
    uuid = request.session['uuid_association']
    association = Association.objects.get(UUID=uuid)
    return association

def assos_part(asso):
    """ retourne les assos partenaire de l'asso organisatrice de l evenement"""
    list_assos = AssoPartenaire.objects.filter(Association=asso)
    return list_assos

def benevoles_par_asso(list_assos):
    """ returne un dictionnaire de nombre de bénévole par asso """
    dic = {}
    for asso in list_assos :
        dic[asso]= ProfileBenevole.objects.filter(assopartenaire=asso).count()
    dic ={k: v for k, v in sorted(dic.items(), key=lambda x: x[1], reverse=True)}
    return dic

def inscription_ouvert(debut, fin):
    """
        prend une date de debut et une date de fin en entree
        en sortie, un integer:
        0: si today avant la période
        1: si today dans la période
        2: si today après la période
    """
    if date.today() < debut:
        return 0
    elif debut <= date.today() <= fin:
        return 1
    else:
        return 2 

################################################
#            views 
################################################

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(user_passes_test(lambda u: u.groups.filter(name__in=['Administrateur','Organisteur','Responsable']).exists()), name='dispatch')
class BenevolesListView(ListView):
    #model = ProfileBenevole
    # benevoles actif 
    queryset = ProfileBenevole.objects.filter(personne__is_active='1')
    template_name = "administration/benevoles.html"
    #paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        print('{} : dispatch'.format(__class__.__name__))
        self.Evt = Evenement.objects.get(UUID=self.request.session['uuid_evenement']) # recuper l evenement
        self.Asso = Association.objects.get(UUID=self.request.session['uuid_association']) # recuper l asso
        # definit les infos a envoyer au tempate
        self.context = { 
            # nav bar infos : debut
            "EvtOuvertBenevoles" : inscription_ouvert(self.Evt.inscription_debut, self.Evt.inscription_fin), # integer précisant si on est avant/dans/après la période de modification des creneaux
            "GroupeUtilisateur" : GroupeUtilisateur(self.request),
            # nav bar infos : fin
            "Association" : self.Asso,
            "Evenement" : self.Evt, 
            "FormPersonne" : PersonneForm(),
            "FormBenevole" : BenevoleForm(), 

            "Benevoles": self.queryset.filter(BenevolesEvenement=self.Evt).order_by('personne__last_name'),  # objets benevoles de l'evenement
            "Administrateurs": ProfileAdministrateur.objects.filter(association=self.Asso),
            "Organisteurs" : ProfileOrganisateur.objects.filter(OrganisateurEvenement=self.Evt),
            "Responsables" : ProfileResponsable.objects.filter(ResponsableEquipe__in=Equipe.objects.filter(evenement=self.Evt)),
        }
        return super().dispatch(request, *args, **kwargs)

    # recupere et traite les données post
    def post(self, request, *args, **kwargs):
        print('{} : post'.format(__class__.__name__))
        print('#########################################################')
        for key, value in request.POST.items():
            print('#        POST -> {0} : {1}'.format(key, value))
        print('#########################################################')

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
                return render(request, self.template_name, self.context )
            else:
                print('erreur de creation de bénévole : {}'.format(formpersonne.errors))
                raise Http404('erreur de creation de bénévole : {}'.format(formpersonne.errors))

        # supprimer un benevole
        if all(k in request.POST for k in ('benevole_supprimer', 'BenevoleUUID')):
            personnesup = get_object_or_404(Personne, UUID=request.POST.get('BenevoleUUID'))
            # secu : on ne supprime les personnes étant également admins
            if  ProfileAdministrateur.objects.filter(personne=personnesup) or \
                ProfileOrganisateur.objects.filter(personne=personnesup) or \
                ProfileResponsable.objects.filter(personne=personnesup):
                print('ne pas supprimer ')
                raise Http404('attention, ne pas supprimer les admins')
            else:
                print('benevole supprimé : {0} {1}'.format(personnesup.last_name, personnesup.first_name))
                benevolesup = get_object_or_404(ProfileBenevole, personne=personnesup).delete()
                personnesup = get_object_or_404(Personne, UUID=request.POST.get('BenevoleUUID')).delete()
                

        # editer un benevole
        if all(k in request.POST for k in ('benevole_editer', 'BenevoleUUID')):
            print('benevole édité : {0} {1}'.format(personnesup.last_name, personnesup.first_name))

        return render(request, self.template_name, self.context)

    # envoi les datas au template
    def get_context_data(self, **kwargs):
        print('{} : get_context_data'.format(__class__.__name__))
        return self.context


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(user_passes_test(lambda u: u.groups.filter(name__in=['Administrateur','Organisteur','Responsable']).exists()), name='dispatch')
class DashboardView(View):
    template_name = "administration/dashboard.html" 

    def dispatch(self, request, *args, **kwargs):
        print('{} : dispatch'.format(__class__.__name__))
        self.Evt = Evenement.objects.get(UUID=self.request.session['uuid_evenement']) # recuper l evenement
        self.Asso = Association.objects.get(UUID=self.request.session['uuid_association']) # recuper l asso
        self.context = { 
            # nav bar infos : debut
            "EvtOuvertBenevoles" : inscription_ouvert(self.Evt.inscription_debut, self.Evt.inscription_fin), # integer précisant si on est avant/dans/après la période de modification des creneaux
            "GroupeUtilisateur" : GroupeUtilisateur(self.request),
            # nav bar infos : fin
            "Association" : self.Asso,
            "Evenement" : self.Evt, 
            "Creneaux" : Creneau.objects.filter(evenement=self.Evt, type="creneau"),
            "Creneaux_libres" : Creneau.objects.filter(evenement=self.Evt, type="creneau", benevole__isnull=True).count,
            "Creneaux_occupes" : Creneau.objects.filter(evenement=self.Evt, type="creneau", benevole__isnull=False).count,
            "Assos_partenaires" : assos_part(self.Asso),
            "benevoles_par_asso" : benevoles_par_asso(assos_part(self.Asso)),

            "Benevoles": ProfileBenevole.objects.filter(BenevolesEvenement=self.Evt),  # objets benevoles de l'evenement
            "Administrateurs": ProfileAdministrateur.objects.filter(association=self.Asso),
            "Organisteurs" : ProfileOrganisateur.objects.filter(OrganisateurEvenement=self.Evt),
            "Responsables" : ProfileResponsable.objects.filter(ResponsableEquipe__in=Equipe.objects.filter(evenement=self.Evt)),
        }
        return super(DashboardView, self).dispatch(request, *args, **kwargs)

    # 
    def get(self, request, *args, **kwargs):
        print('{} : get_context_data'.format(__class__.__name__))
        return render(request, self.template_name, self.context)

    # envoi les datas au template
    #def get_context_data(self, **kwargs):
    #    print('{} : get_context_data'.format(__class__.__name__))
    #    return self.context
