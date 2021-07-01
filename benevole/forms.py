from django.forms import widgets
from django.forms.widgets import HiddenInput
from evenement.customwidgets import SplitDateTimeMultiWidget
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django import forms
from django.forms import ModelForm
from django.forms.fields import DateField, DateTimeField
from benevole.models import ProfileBenevole, Personne
import uuid

# pour date picker
class DateInput(forms.DateInput):
    input_type = 'date'

# forms d'enregistrement
class RegisterForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ['email', 'username', 'last_name', 'first_name', 'password1', 'password2']
        exclude = ['username', 'last_name', 'first_name']

    def save(self):
        # genere un username aleatoire pour remplir le champs, pas utilisé vu qu'on utilise email pour se logguer
        self.instance.username = uuid.uuid4().hex[:16].upper()
        return super(RegisterForm, self).save()

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Email')

class BenevoleForm(ModelForm):
    class Meta:
        model = ProfileBenevole
        fields = ['message', 'assopartenaire', 'personne']
        exclude = ['personne',]

    def save(self, personne):
        # on force le champs personne_id vu que j'y arrive pas par la view
        print('personne {}'.format(personne.UUID))
        self.instance.personne = personne
        return super(BenevoleForm, self).save()


class PersonneForm(ModelForm):
    date_de_naissance = DateField(widget=DateInput())

    class Meta:
        model = Personne
        fields = ['last_name', 'first_name', 'genre', 'date_de_naissance', 'email', 'portable', 'description']
        exclude = ['description',]