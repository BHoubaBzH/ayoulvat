from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# test phil premiere page
from association.models import Association


@login_required(login_url='login')
def liste_assos(request):
    """
    liste toutes les assosciations,a filtrer par assos affectées au gestionnaire
    """
    data = {
        "Assos": Association.objects.all(),

    }
    return render(request, "association/associations_liste.html", data)


@login_required(login_url='login')
def detail_asso(request, uuid_asso):
    """
    affiche une asso spécifique
    """
    # store dans la session le uuid de l'asso
    request.session['uuid_association'] = uuid_asso

    association = Association.objects.get(UUID_association= uuid_asso)
    data = {
        "Asso": association,
    }
    return render(request, "association/association_detail.html", data)
