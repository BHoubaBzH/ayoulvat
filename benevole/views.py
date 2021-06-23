from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic

from benevole.forms import RegisterForm


class InscriptionView(generic.CreateView):
    #form_class = UserCreationForm
    form_class = RegisterForm               # on utilise notre form custom
    success_url = reverse_lazy('login')
    template_name = 'benevole/inscription.html'

