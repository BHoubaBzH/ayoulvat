from django.forms import ModelForm, DateTimeField, HiddenInput, ValidationError
from django.forms import ModelChoiceField, ModelMultipleChoiceField, CheckboxSelectMultiple

from evenement.models import Poste, Creneau, Planning
from benevole.models import ProfileBenevole
from evenement.customwidgets import SplitDateTimeMultiWidget


class PosteForm(ModelForm):
    benevole = ModelMultipleChoiceField(queryset=ProfileBenevole.objects.all(),
                                        required=False,
                                        widget=CheckboxSelectMultiple)

    class Meta:
        model = Poste
        # exclude = [ 'planning', ]
        # fields = '__all__'
        # ordonne l affichage des champs
        fields = ['nom', 'description', 'couleur', 'editable', 'benevole', 'planning', 'equipe', 'evenement']

    # cache certains champs
    def __init__(self, *args, **kwargs):
        super(PosteForm, self).__init__(*args, **kwargs)
        self.fields['planning'].widget = HiddenInput()
        self.fields['equipe'].widget = HiddenInput()
        self.fields['evenement'].widget = HiddenInput()


class CreneauForm(ModelForm):
    # Query set doit prendre que les benevoles inscrits sur l evenement : a faire
    # voir aussi par équipe et par planning
    benevole = ModelChoiceField(queryset=ProfileBenevole.objects.all(),
                                required=False,
                                empty_label="Libre")
    debut = DateTimeField(widget=SplitDateTimeMultiWidget())
    fin = DateTimeField(widget=SplitDateTimeMultiWidget())

    class Meta:
        model = Creneau
        # exclude = ['benevole',]
        fields = ['debut', 'fin', 'description', 'editable', 'benevole', 'poste', 'planning', 'equipe', 'evenement']

    # methode __init__ surcharge les definition précédente de la class
    def __init__(self, *args, **kwargs):
        self.pas_creneau = kwargs.pop('pas_creneau')
        self.planning_uuid = kwargs.pop('planning_uuid')
        super(CreneauForm, self).__init__(*args, **kwargs)
        # cache certains champs
        self.fields['poste'].widget = HiddenInput()
        self.fields['planning'].widget = HiddenInput()
        self.fields['equipe'].widget = HiddenInput()
        self.fields['evenement'].widget = HiddenInput()
        instance = getattr(self, 'instance', None)
        if instance:
            pass  # self.fields['debut'].disabled = True
        # recuperer le pas du planning associé
        # time_attr.step :  valeurs valides liées au pas du planning dans les choix en unités secondes :
        # ex 30 * 60 = 1800 : toutes les 30 minutes sont OK
        self.fields['debut'].widget = \
            SplitDateTimeMultiWidget(attrs={
                                            'date_attrs': {},
                                            'time_attrs': {'step': (self.pas_creneau * 60).__str__()}
                                            })
        self.fields['fin'].widget = \
            SplitDateTimeMultiWidget(attrs={
                                            'date_attrs': {},
                                            'time_attrs': {'step': (self.pas_creneau * 60).__str__()}
                                            })
        # on ne propose que les bénévoles etant inscrit sur le planning = fk du planning
        # il faut aussi ajouter seulement les benevoles disponibles ( non pris sur un autre creneau aux meme heures)
        self.fields['benevole'].queryset = ProfileBenevole.objects.filter(BenevolesPlanning=self.planning_uuid)

    # on valided les données pour avoir de la cohérence
    def clean_debut(self):
        debut = self.cleaned_data['debut']
        Plan = Planning.objects.get(UUID_planning=self.planning_uuid)
        planning_debut = Plan._meta.get_field('debut')
        if debut < planning_debut.value_from_object(Plan):
            raise ValidationError("Wopolo ca peut pas etre avant le début du planning!")
        return debut
    def clean_fin(self):
        fin = self.cleaned_data['fin']
        debut = self.cleaned_data['debut']
        Plan = Planning.objects.get(UUID_planning=self.planning_uuid)
        planning_fin = Plan._meta.get_field('fin')
        print("form fin : {}".format(fin))
        print("form debut : {}".format(debut))
        if fin > planning_fin.value_from_object(Plan):
            raise ValidationError("Wopolo ca peut pas finir après la fin du planning!")
        if debut >= fin:
            raise ValidationError("Wopolo la fin du creneau c'est après son début!")
        return fin
