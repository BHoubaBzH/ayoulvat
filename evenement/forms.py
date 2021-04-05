from django import forms
from phonenumber_field.formfields import PhoneNumberField

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