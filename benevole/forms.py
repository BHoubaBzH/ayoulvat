from django.contrib.auth.models import User
from django.forms import ValidationError, widgets
from django.forms.models import inlineformset_factory
from django.forms.widgets import HiddenInput
from evenement.customwidgets import SplitDateTimeMultiWidget
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django import forms
from django.forms import ModelForm
from django.forms.fields import DateField, DateTimeField
from random import randint
from benevole.models import ProfileBenevole, Personne
from ayoulvat.languages import text_template

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

# pour date picker
class DateInput(forms.DateInput):
    input_type = 'date'

################################################################################################
# forms d'enregistrement
################################################################################################
class RegisterForm(UserCreationForm):

    class Meta:
        model = get_user_model()
        fields = ['email', 'username', 'password1', 'password2']
        exclude = ['username']

    def save(self):
        # genere un username aleatoire pour remplir le champs, pas utilisé vu qu'on utilise email pour se logguer
        # self.instance.username = uuid.uuid4().hex[:16].upper()
        # met le mail au niveau du username
        self.instance.username = self.instance.email
        return super().save()

################################################################################################
#class LoginForm(AuthenticationForm):
#    username = forms.CharField(label='Email')

################################################################################################
class BenevoleForm(ModelForm):
    class Meta:
        model = ProfileBenevole
        fields = ['message', 'personne']
        exclude = ['personne',]

    def save(self, personne, commit=True):
        # on lie le benevole à la personne
        # print('personne {}'.format(personne.UUID))
        self.instance.personne = personne
        if commit:
            return super().save()
        else:
            return super().save(commit=False)        

################################################################################################
class PersonneForm(ModelForm):
    date_de_naissance = DateField(widget=DateInput(format='%Y-%m-%d'))

    class Meta:
        model = Personne
        fields = ['last_name', 'first_name', 'genre', 'date_de_naissance', 'email', 'portable', 'description']
        exclude = ['description',]

    def save(self, commit=True): # si pas indiqué commit est à true

        if not self.instance.username:
            # met le mail au niveau du username, on vient de la page benevole
            self.instance.username = self.instance.email
        if not self.instance.email:
            # on vient de la page admin, pas d email renseigné
            email1 = ''.join(letter for letter in self.instance.first_name if letter.isalnum()).lower() 
            email2 = ''.join(letter for letter in self.instance.last_name if letter.isalnum()).lower()
            email3 = randint(10, 99)
            self.instance.email = f'{email1}.{email2}@acme{email3}.bzh'
            self.instance.username = self.instance.email

        if commit:
            if not self.instance.password:
                self.instance.password = 'mot_de_passe_temporaire'
            return super().save()
        else:
            return super().save(commit=False)        

    #def clean(self):
    #    super().clean()
    #    email = self.cleaned_data['email']
    #    #list_personnes = Personne.objects.all().values_list("username", flat=True)
    #    if Personne.objects.filter(username=email).exists():
    #        raise ValidationError(f"{email} existe deja")
        
class PersonneFormAdmin(PersonneForm):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields['email'].required = False
        self.fields['email'].help_text = 'Optionnel'
        self.fields['portable'].required = True
        self.fields['portable'].help_text = 'Obligatoire'
        self.fields['date_de_naissance'].initial = '1900-01-01'
        self.fields['date_de_naissance'].required = False
