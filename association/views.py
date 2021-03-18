from django.shortcuts import render



# test phil premiere page
from association.models import Association


def ShowAsso(request):
    data = {
        "Assos": Association.objects.all(),

    }
    return render(request, "association/show_asso.html", data)