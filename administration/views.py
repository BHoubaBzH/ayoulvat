import logging
from django.http.response import Http404, HttpResponseServerError
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from benevole.forms import BenevoleForm, PersonneForm
from evenement.models import Evenement
from evenement.views import inscription_ouvert
from benevole.views import GroupeUtilisateur
from benevole.models import Personne, ProfileBenevole
from association.models import Association

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

################################################
#            views 
################################################

@login_required(login_url='login')
@user_passes_test(lambda u: u.groups.filter(name__in=['Administrateur','Organisteur','Responsable']).exists())
def benevoles_liste(request):
    # log les donnees post
    print('#########################################################')
    for key, value in request.POST.items():
        print('#        POST -> {0} : {1}'.format(key, value))
    print('#########################################################')

    Asso = association(request)
    Evt = evenement(request)
    # request.session['uuid_association']
    data = { 
        "Association" : Asso,
        "Evenement" : Evt, # recuper l evenement
        #nav bar infos
        "EvtOuvertBenevoles" : inscription_ouvert(Evt.inscription_debut, Evt.inscription_fin), # integer précisant si on est avant/dans/après la période de modification des creneaux
        "GroupeUtilisateur" : GroupeUtilisateur(request),
        # fin nav bar infos
        "FormPersonne" : PersonneForm(),
        "FormBenevole" : BenevoleForm(), 
        "benevole_formset" : BenevoleCreationFormSet(), # formset vide non lié pour creation
        "Benevoles": ProfileBenevole.objects.filter(BenevolesEvenement=Evt),  # objets benevoles de l'evenement
        }
    # benevole_formset = BenevoleCreationFormSet() # formset vide non lié pour creation
    if request.method == "POST":
        if 'benevole_creer' in request.POST:
            formpersonne = PersonneForm(request.POST)
            if formpersonne.is_valid():
                personne = formpersonne.save(commit=False)
                benevole_formset = BenevoleCreationFormSet(request.POST,instance=personne)
                if benevole_formset.is_valid():
                    print("benevole création")
                    formpersonne.save()
                    benevole_formset.save()
                    # cree le lien evenement - benevole
                    temp_evt = Evenement.objects.get(UUID=request.session['uuid_evenement'])
                    ### comment faire le lien entre l evenement et le profilebenevole qui vient d' etre créé??? #####
                    ### en attendant, on prend le dernier qui a joint , donc normalement celui que nous sommes en train de creer ###
                    plop = ProfileBenevole.objects.get(personne_id=Personne.objects.filter().order_by('-date_joined').first())
                    # ajoute notre benevole dans le champs manytomany 
                    temp_evt.benevole.add(ProfileBenevole.objects.get(UUID=plop.UUID)) 
                else:
                    raise Http404('<h1>Problème de création de Bénévole</h1>')

    # data["benevole_formset"]= benevole_formset

    return render(request, "administration/benevoles.html", data)


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(user_passes_test(lambda u: u.groups.filter(name__in=['Administrateur','Organisteur','Responsable']).exists()), name='dispatch')
class BenevolesListView(ListView):
    #model = ProfileBenevole
    queryset = ProfileBenevole.objects.all()
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
            "Benevoles": ProfileBenevole.objects.filter(BenevolesEvenement=self.Evt),  # objets benevoles de l'evenement
        }
        return super().dispatch(request, *args, **kwargs)

    # recupere les données post
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

