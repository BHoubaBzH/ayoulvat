from django.forms import widgets
from django.forms.widgets import HiddenInput
from evenement.customwidgets import SplitDateTimeMultiWidget
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django import forms
from django.forms import ModelForm
from django.forms.fields import DateField, DateTimeField
from benevole.models import ProfileBenevole, Personne

# pour date picker
class DateInput(forms.DateInput):
    input_type = 'date'

# forms d'enregistrement
class RegisterForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('email', 'username', 'last_name', 'first_name', 'password1', 'password2')


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Email')

class BenevoleForm(ModelForm):
    class Meta:
        model = ProfileBenevole
        fields = ['message', 'assopartenaire', 'personne']
        exclude = ['personne',]


class PersonneForm(ModelForm):
    date_de_naissance = DateField(widget=DateInput())

    class Meta:
        model = Personne
        fields = ['last_name', 'first_name', 'genre', 'date_de_naissance', 'email', 'portable', 'description']
        exclude = ['description',]