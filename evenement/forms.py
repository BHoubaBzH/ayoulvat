from django.forms import ModelForm, HiddenInput
from phonenumber_field.formfields import PhoneNumberField
from evenement.models import Poste

class PosteForm(ModelForm):
    class Meta:
        model = Poste
        # exclude = [ 'planning', ]
        # fields = '__all__'
        # ordonne l affichage des champs
        fields = [ 'planning', 'nom', 'description', 'couleur', 'editable', 'benevole' ]

    # cache le planning vu que nous l avons deja choisi
    def __init__(self, *args, **kwargs):
        super(PosteForm, self).__init__(*args, **kwargs)
        self.fields['planning'].widget = HiddenInput()


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
