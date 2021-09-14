import logging
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.translation import templatize

from benevole.forms import BenevoleCreationFormSet, BenevoleForm, PersonneForm
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
            if formpersonne.is_valid:
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

    # data["benevole_formset"]= benevole_formset

    return render(request, "administration/benevoles.html", data)



@login_required(login_url='login')
@user_passes_test(lambda u: u.groups.filter(name__in=['Administrateur','Organisteur','Responsable']).exists())
def benevole_edite(request):
    data = { "test" : 'plop', }
    return render(request, "administration/benevole/edite.html", data)


@login_required(login_url='login')
@user_passes_test(lambda u: u.groups.filter(name__in=['Administrateur','Organisteur','Responsable']).exists())
def benevole_supprime(request):
    data = { "test" : 'plop', }
    return render(request, "administration/benevole/supprime.html", data)
