from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

from association.models import Association
from benevole.models import ProfileAdministrateur

@login_required(login_url='login')
def liste_assos(request):
    """
    liste toutes les assosciations,a filtrer par assos affectées a administrateur
    """
    data = {
        #"Assos": Association.objects.all(),
        # attention ok car on ne peut estre admin que d un evenement
        "Assos" : [request.user.profileadministrateur.association],
    }
    return render(request, "association/associations_liste.html", data)


@login_required(login_url='login')
def detail_asso(request, uuid_asso):
    """
    affiche une asso spécifique
    """
    # store dans la session le uuid de l'asso
    request.session['uuid_association'] = uuid_asso.urn

    association = Association.objects.get(UUID=uuid_asso)
    #benevoles_l = Personne.objects.select_related("profilebenevole", "profileresponsable", "profileorganisateur", "profileadministrateur").all()
    data = {
        "Association": association,
    }

    print(' details de l asso : '.format(association.UUID))
    return render(request, "association/association_detail.html", data)
