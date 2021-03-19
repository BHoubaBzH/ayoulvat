from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# test phil premiere page
from association.models import Association


@login_required(login_url='/ayoulvat/login')
def ShowAsso(request):
    data = {
        "Assos": Association.objects.all(),

    }
    return render(request, "association/show_asso.html", data)