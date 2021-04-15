from django.forms import ModelForm, HiddenInput, ModelChoiceField
from phonenumber_field.formfields import PhoneNumberField
from evenement.models import Poste, Creneau
from benevole.models import ProfileBenevole, Personne


class PosteForm(ModelForm):
    class Meta:
        model = Poste
        # exclude = [ 'planning', ]
        # fields = '__all__'
        # ordonne l affichage des champs
        fields = [ 'nom', 'description', 'couleur', 'editable', 'benevole', 'planning', 'equipe', 'evenement' ]

    # cache certains champs
    def __init__(self, *args, **kwargs):
        super(PosteForm, self).__init__(*args, **kwargs)
        self.fields['planning'].widget = HiddenInput()
        self.fields['equipe'].widget = HiddenInput()
        self.fields['evenement'].widget = HiddenInput()


class CreneauForm(ModelForm):
    # Query set doit prendre que les benevoles inscrits sur l envenement : a faire
    # voir aussi par équipe et par planning
    benevole = ModelChoiceField(queryset=ProfileBenevole.objects.all(), required=False, empty_label="Vide")
    class Meta:
        model = Creneau
        # exclude = ['benevole', ]
        fields = ['debut', 'fin', 'description', 'editable', 'benevole', 'poste', 'planning', 'equipe', 'evenement' ]
    # cache certains champs
    def __init__(self, *args, **kwargs):
        super(CreneauForm, self).__init__(*args, **kwargs)
        #self.fields['poste'].widget = HiddenInput()
        #self.fields['planning'].widget = HiddenInput()
        #self.fields['equipe'].widget = HiddenInput()
        #self.fields['evenement'].widget = HiddenInput()

class BenevoleForm(ModelForm):
    class Meta:
        model = ProfileBenevole
        fields = ['message', 'personne']


class PersonneForm(ModelForm):
    class Meta:
        model = Personne
        fields = ['last_name', 'first_name', 'genre', 'date_de_naissance',
                  'assoorigine', 'email', 'portable', 'description']

"""
class CreneauDetails(forms.Form):
    date = forms.DateField()
    debut = forms.TimeField()
    fin = forms.TimeField()
    duree = forms.TimeField()
    # equipe = forms.CharField(max_length=100)
    benevole = forms.CharField(max_length=100)
    genre = forms.CharField(max_length=50)
    date_de_naissance = forms.DateField()
    asso_origine = forms.CharField(max_length=100)
    courriel = forms.EmailField()
    portable = PhoneNumberField()
"""
