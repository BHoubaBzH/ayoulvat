from benevole.models import Personne, ProfileBenevole
from evenement.models import Evenement
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from benevole.forms import BenevoleForm, PersonneForm, RegisterForm


# nouvelle class d'enregistrement 
class InscriptionView(generic.CreateView):
    #form_class = UserCreationForm
    form_class = RegisterForm               # on utilise notre form custom
    success_url = reverse_lazy('login')
    template_name = 'benevole/inscription.html'


def Home(request):
    """
        page profile de login et principale du benevole
    """
    data = {
        "FormPersonne" : PersonneForm(),  # form personne non liée
        "Evenements" : Evenement.objects.all(),  # liste de tous les evenements
    }
    # récupère dans la session l'uuid de l'association, si on est passé par l'asso
    try:
        uuid_evenement = request.session['uuid_evenement']
        print('evenement : {}'.format(uuid_evenement))
        evenement = Evenement.objects.get(UUID=uuid_evenement)
        #data["Evenement"] = evenement
        data["Benevoles"] = ProfileBenevole.objects.filter(BenevolesEvenement=evenement)  # objets benevoles de l'evenement
    except:
        print('on est pas passé la page evenement')

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

    if request.method == "POST" and request.POST.get('personne'):
        # si on a de donnes post, on sauvegarde les formulaires
        FormPersonne = PersonneForm(request.POST, instance=Personne.objects.get(UUID=request.POST.get('personne')))
        FormBenevole = BenevoleForm(request.POST, instance=ProfileBenevole.objects.get(personne_id=request.user.UUID))
        if FormBenevole.is_valid() and FormPersonne.is_valid():
            print('bénévole modifié')
            FormBenevole.save()
            FormPersonne.save()    

    # on construit nos objets a passer au template dans le dictionnaire data
    data = {
        "FormPersonne" : PersonneForm(instance=Personne.objects.get(UUID=request.user.UUID)),  # form personne liée
        "FormBenevole" : BenevoleForm(instance=ProfileBenevole.objects.get(personne_id=request.user.UUID)), # form benevole liée
        "Evenements" : "",  # liste de tous les evenements
    }

    return render(request, "benevole/profile.html", data)