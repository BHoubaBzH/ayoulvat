import collections
from datetime import date, datetime, time, timedelta
import logging
from django.http.response import Http404, HttpResponseServerError
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views.generic import ListView, View
from django.db.models import Q
import benevole

from benevole.forms import BenevoleForm, PersonneForm
from evenement.models import Creneau, Equipe, Evenement, Planning, evenement_benevole_assopart
#from evenement.views import inscription_ouvert
from benevole.models import Personne, ProfileAdministrateur, ProfileBenevole, ProfileOrganisateur, ProfileResponsable
from association.models import AssoPartenaire, Association

from django.shortcuts import render
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

def assos_part(evt):
    """ retourne Qeuryset des assos partenaire de l evenement"""
        # liste de uuid des assos partenaire de l evenement, retire le none (sans asso) de la liste 
    list_uuid = evenement_benevole_assopart.objects.filter(Q(evenement=evt),~Q(asso_part=None)).values_list('asso_part', flat=True).distinct()
    list_assos = AssoPartenaire.objects.filter(UUID__in=list_uuid)
    return list_assos

def total_heures_benevoles(creneaux):
    """ total d'heures de bénévolat sur l'évènement retourne un timedelta """
    total = timedelta(0, 0, 0, 0)
    for c in creneaux:
        if c.benevole:
            c_duree = c.fin - c.debut
            total += c_duree
    return total

def nb_creneaux_par_benevole(evt, benevoles):
    """ out dictionnaire: objet benevole - nombre de creneaux """
    out={}
    for benevole in benevoles: 
        out[benevole]=Creneau.objects.filter(Q(benevole=benevole),Q(evenement=evt)).count()
    return out


def nb_benevoles_par_asso(list_assos, evt):
    """ returne un dictionnaire de nombre de bénévole par asso sur l evenement"""
    dic = {}
    for asso in list_assos:
        dic[asso] = evenement_benevole_assopart.objects.filter(Q(asso_part=asso),Q(evenement=evt)).count()
    dic['Sans association'] = evenement_benevole_assopart.objects.filter(Q(asso_part=None),Q(evenement=evt)).count()
    dic ={k: v for k, v in sorted(dic.items(), key=lambda x: x[1], reverse=True)}
    return dic

def plannings_occupation(contenants):
    """
        retoune le taux d'occupation par contenant 
        entree : queryset de contenants
        sortie : dictionnaire key : contenant , value : pourcentage occupation
    """
    occup = {}
    for c in contenants:
        crens = Creneau.objects.filter(planning_id=c.UUID).count()
        crens_occup = Creneau.objects.filter(planning_id=c.UUID, benevole__isnull=False).count()
        pourcentage = (crens_occup / crens) * 100 if crens != 0 else 0
        occup[c] = round(pourcentage, 1)
    return occup

def equipes_occupation(contenants):
    """ 
        retoune le taux d'occupation par contenant 
        entree : queryset de contenants
        sortie : dictionnaire key : contenant , value : pourcentage occupation
    """
    occup = {}
    for c in contenants:
        crens = Creneau.objects.filter(equipe_id=c.UUID).count()
        crens_occup = Creneau.objects.filter(equipe_id=c.UUID, benevole__isnull=False).count()
        pourcentage = (crens_occup / crens) * 100 if crens != 0 else 0
        occup[c] = round(pourcentage, 1)
    return occup

def repartition_par_assos(creneaux):
    """ 
        retoune la répartition horaire par assos
        entree : queryset des creneaux de l evenement
        sortie : dictionnaire key : assos , pourcentage total
    """
    repart = {}
    total = total_heures_benevoles(creneaux)

    for c in creneaux:
        #print('ev ', c, c.evenement.UUID)
        #print('ben', c, c.benevole.UUID)
        #print(evenement_benevole_assopart.objects.get(Q(evenement=c.evenement),Q(profilebenevole=c.benevole)).asso_part)
        try:
            # on a un evenement, un benevole et une asso_prt de liés
            asso_du_creneau=evenement_benevole_assopart.objects.get(Q(evenement=c.evenement),Q(profilebenevole=c.benevole)).asso_part
        except:
            # on a pas de lien
            pass
        if asso_du_creneau:
            c_duree = c.fin - c.debut
            # print('{} : {}'.format(c.benevole.assopartenaire, c_duree))
            try:
                repart[asso_du_creneau.nom] += c_duree
            except:
                repart[asso_du_creneau.nom] = c_duree
            # print('{} : {}'.format(c.benevole.assopartenaire, repart[c.benevole.assopartenaire]))
        else:
            c_duree = c.fin - c.debut
            try:
                repart["sans association"] += c_duree
            except:
                repart["sans association"] = c_duree
    for rep, val in repart.items():
        repart[rep] = round(val / total *100, 1)
        # print('{} : {}'.format(rep, repart[rep]))
    return dict(sorted(repart.items(), key=lambda item: item[1],reverse=True))

def emails_benevoles_evenement(evt):
    """
        sortie : liste emails des bénévoles ayant pris un créneau
    """
    listout = []
    for bene in ProfileBenevole.objects.filter(BenevolesCreneau__evenement=evt).prefetch_related('BenevolesCreneau').select_related('personne'):
            email = bene.personne.email
            listout.append(email)
    return set(listout)

def emails_benevoles_sans_creneaux(evt):
    """
        sortie : liste emails des bénévoles sans créneau
    """
    listout = []
    for bene in ProfileBenevole.objects.all().exclude(BenevolesCreneau__evenement=evt).prefetch_related('BenevolesCreneau').select_related('personne'):
            email = bene.personne.email
            listout.append(email)
    return set(listout)

def emails_benevoles_un_creneau(evt):
    """
        sortie : liste emails des bénévoles ayant choisi un seul créneau
    """ 
    listtemp = []
    listout = []
    for bene in ProfileBenevole.objects.filter(BenevolesCreneau__evenement=evt).prefetch_related('BenevolesCreneau').select_related('personne'):
            email = bene.personne.email
            listtemp.append(email)
    #print(listtemp)
    #print(dict(collections.Counter(listtemp)))
    for key, val in dict(collections.Counter(listtemp)).items():
        if val == 1:
            listout.append(key)
    return set(listout)

def emails_benevoles_par_equipe(evt):
    """
        sortie : dictionnaire de liste emails , clés : equipes
    """
    tabout = {}
    for equipe in list(Equipe.objects.filter(evenement=evt)):
        liste_emails = []
        for bene in ProfileBenevole.objects.filter(BenevolesCreneau__equipe=equipe).prefetch_related('BenevolesCreneau').select_related('personne'):
            email = bene.personne.email
            liste_emails.append(email)
            if liste_emails:
                tabout[equipe] = set(liste_emails)
    #for k, v in tabout.items():
    #    print(k)
    #    print(*v)
    return tabout

def emails_benevoles_par_planning(evt):
    """
        sortie : dictionnaire de liste[ equipe, planning nom, [liste emails]] , clés : plannings
    """
    tabout = {}
    for planning in list(Planning.objects.filter(evenement=evt).order_by("debut")):
        liste_emails = []
        liste_planning = []
        #for bene in ProfileBenevole.objects.filter(BenevolesCreneau__planning=planning):
        for bene in ProfileBenevole.objects.filter(BenevolesCreneau__planning=planning).prefetch_related('BenevolesCreneau').select_related('personne'):
            email = bene.personne.email
            liste_emails.append(email)
        liste_planning.append(planning.equipe)
        liste_planning.append(planning.nom)
        liste_planning.append(set(liste_emails))
        tabout[planning] = liste_planning
    return tabout

def emails_responsables(evt):
    """
        sortie : liste emails des bénévoles responsables sur l'evenement
    """
    listout = []
    for bene in ProfileBenevole.objects.filter(BenevolesEvenement=evt, personne__groups__name__in=['Responsable','Organisateur','Administrateur']):
            email = bene.personne.email
            listout.append(email)
    return set(listout)

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
        self.ListeBenevoles = self.queryset.select_related('personne').filter(BenevolesEvenement=self.Evt).order_by('personne__last_name')  # objets benevoles de l'evenement
        # definit les infos a envoyer au tempate
        self.context = { 
            # nav bar infos : debut
            "EvtOuvertBenevoles" : inscription_ouvert(self.Evt.inscription_debut, self.Evt.inscription_fin), # integer précisant si on est avant/dans/après la période de modification des creneaux
            # nav bar infos : fin
            "Association" : self.Asso,
            "Evenement" : self.Evt, 
            "FormPersonne" : PersonneForm(),
            "FormBenevole" : BenevoleForm(), 

            "Equipes" : Equipe.objects.filter(evenement=self.Evt).order_by('nom'),

            "Benevoles": self.ListeBenevoles,
            "NbCreneauxParBenevole": nb_creneaux_par_benevole(self.Evt, self.ListeBenevoles), 
            "EvtBeneAssopar": evenement_benevole_assopart.objects.filter(evenement=self.Evt),
            "Administrateurs": ProfileAdministrateur.objects.select_related('personne').filter(association=self.Asso),
            "Organisteurs" : ProfileOrganisateur.objects.select_related('personne').filter(OrganisateurEvenement=self.Evt),
            "Responsables" : ProfileResponsable.objects.select_related('personne').filter(ResponsableEquipe__in=Equipe.objects.filter(evenement=self.Evt)),

            "Emails_benevoles_par_planning" : emails_benevoles_par_planning(self.Evt),
            "Emails_benevoles_par_equipe" : emails_benevoles_par_equipe(self.Evt),
            "Emails_benevoles_evenement" : emails_benevoles_evenement(self.Evt),
            "Emails_benevoles_sans_creneaux" : emails_benevoles_sans_creneaux(self.Evt),
            "Emails_benevoles_un_creneau" : emails_benevoles_un_creneau(self.Evt),
            "Emails_responsables" : emails_responsables(self.Evt),
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
                #return render(request, self.template_name, self.context )
            else:
                print('erreur de creation de bénévole : {}'.format(formpersonne.errors))
                raise Http404('erreur de creation de bénévole : {}'.format(formpersonne.errors))
            ### ajouter la possibilité de lier à un benevole existant deja
            ###             creer lien evenement-profilebenevole
            ### ajouter la possibilite de lier à une personne dans profilebenevole
            ###             creer profilebenevole + line evenement-profilebenevole 

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
        # recharge les liste infos pour mettre à jour suite aux modifs ( creation ou suppression de benevole)
        self.context['Benevoles']=self.queryset.select_related('personne').filter(BenevolesEvenement=self.Evt).order_by('personne__last_name')
        self.context['NbCreneauxParBenevole']= nb_creneaux_par_benevole(self.Evt, self.context['Benevoles'])
            

        # editer un benevole
        #personnesup = get_object_or_404(Personne, UUID=request.POST.get('BenevoleUUID'))
        #if all(k in request.POST for k in ('benevole_editer', 'BenevoleUUID')):
        #    print('benevole édité : {0} {1}'.format(personnesup.last_name, personnesup.first_name))
 
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
        self.queryset_c = Creneau.objects.filter(evenement=self.Evt, type="creneau") # les creneau de l evenement
        self.context = {
            # nav bar infos : debut
            "EvtOuvertBenevoles" : inscription_ouvert(self.Evt.inscription_debut, self.Evt.inscription_fin), # integer précisant si on est avant/dans/après la période de modification des creneaux

            # nav bar infos : fin
            "Association" : self.Asso,
            "Evenement" : self.Evt, 
            "Plannings": Planning.objects.filter(evenement=self.Evt).order_by('debut'),  # objets planning de l'evenement
            "Creneaux" : self.queryset_c,
            "Creneaux_libres" : Creneau.objects.filter(evenement=self.Evt, type="creneau", benevole__isnull=True).count,
            "Creneaux_occupes" : Creneau.objects.filter(evenement=self.Evt, type="creneau", benevole__isnull=False).count,
            "Assos_partenaires" : assos_part(self.Evt), # partenaire de l evenement
            "Benevoles_par_asso" : nb_benevoles_par_asso(assos_part(self.Evt), self.Evt),
            "Plannings_occupation" : plannings_occupation(Planning.objects.filter(evenement=self.Evt).order_by('equipe__nom','debut')),
            "Equipes_occupation" : equipes_occupation(Equipe.objects.filter(evenement=self.Evt).order_by('nom')),
            "Repartition_par_assos" : repartition_par_assos(self.queryset_c.filter(benevole__isnull=False)),
            "Total_heures_benevoles" : '{}'.format(total_heures_benevoles(self.queryset_c.filter(benevole__isnull=False)).total_seconds()/3600),

            "Benevoles": ProfileBenevole.objects.filter(BenevolesEvenement=self.Evt),  # objets benevoles inscrits à l'evenement
            "Benevoles_c": self.queryset_c.filter(benevole__isnull=False).values('benevole_id').distinct(), # objets benevoles inscrits à l'evenement avec au moins un creneau
            "Administrateurs": ProfileAdministrateur.objects.filter(association=self.Asso),
            "Organisteurs" : ProfileOrganisateur.objects.filter(OrganisateurEvenement=self.Evt),
            "Responsables" : ProfileResponsable.objects.filter(ResponsableEquipe__in=Equipe.objects.filter(evenement=self.Evt)),
        }
        return super().dispatch(request, *args, **kwargs)

    #  
    def get(self, request, *args, **kwargs):
        print('{} : get_context_data'.format(__class__.__name__))
        return render(request, self.template_name, self.context)

