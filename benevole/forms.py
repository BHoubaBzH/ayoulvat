from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django import forms
from django.forms import ModelForm
from benevole.models import ProfileBenevole, Personne

# forms d'enregistrement
class RegisterForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('email', 'username', 'last_name', 'first_name', 'password1', 'password2')


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Email / Username')

class BenevoleForm(ModelForm):
    class Meta:
        model = ProfileBenevole
        fields = ['message', 'personne']


class PersonneForm(ModelForm):
    class Meta:
        model = Personne
        fields = ['last_name', 'first_name', 'genre', 'date_de_naissance',
                  'assoorigine', 'email', 'portable', 'description']
