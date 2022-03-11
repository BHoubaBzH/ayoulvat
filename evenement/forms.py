from datetime import datetime

from django.db.models.query import QuerySet
from benevole.forms import PersonneForm
from uuid import UUID
from django.forms import ModelForm, DateTimeField, HiddenInput, ValidationError
from django.forms import ModelChoiceField, ModelMultipleChoiceField, CheckboxSelectMultiple
from django_range_slider.fields import RangeSliderField
from django.db.models import Q,F

from evenement.models import Equipe, Evenement, Planning, Poste, Creneau
from benevole.models import Personne, ProfileBenevole
from evenement.customwidgets import SplitDateTimeMultiWidget

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)
################################################################################################
class EquipeForm(ModelForm):
    class Meta:
        model = Equipe
        fields = '__all__'
        fields = ['nom',
                  'responsable_valide',
                  'responsable_creer',
                  'description',
                  'editable',
                  'couleur',
                  'seuil1',
                  'seuil2',
                  'evenement',]
                
    # cache certains champs
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # pas encore codé, on cache le champs
        self.fields['editable'].widget = HiddenInput()
        self.fields['seuil1'].widget.attrs['min'] = '0'
        self.fields['seuil1'].widget.attrs['max'] = '100'
        self.fields['seuil2'].widget.attrs['min'] = '0'
        self.fields['seuil2'].widget.attrs['max'] = '100'

################################################################################################
class PlanningForm(ModelForm):
    debut = DateTimeField(widget=SplitDateTimeMultiWidget())
    fin = DateTimeField(widget=SplitDateTimeMultiWidget())
    class Meta:
        model = Planning
        fields = ['nom',
                  'debut',
                  'fin',
                  'creneaux',
                  'ouvert_mineur',
                  'pas',
                  'creneau_moyen',
                  'description',
                  'editable',
                  'couleur',
                  'seuil1',
                  'seuil2',
                  'equipe',
                  'evenement',
                  ]

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        # pas encore codé, on cache le champs
        self.fields['editable'].widget = HiddenInput()
        self.fields['ouvert_mineur'].widget = HiddenInput()
        self.fields['seuil1'].widget.attrs['min'] = '0'
        self.fields['seuil1'].widget.attrs['max'] = '100'
        self.fields['seuil2'].widget.attrs['min'] = '0'
        self.fields['seuil2'].widget.attrs['max'] = '100'
        #self.fields['equipe'].disabled = True
        #self.fields['evenement'].disabled = True


################################################################################################
class PosteForm(ModelForm):
    benevole = ModelMultipleChoiceField(queryset=ProfileBenevole.objects.all(),
                                        required=False,
                                        widget=CheckboxSelectMultiple)

    class Meta:
        model = Poste
        # exclude = [ 'planning', ]
        # fields = '__all__'
        # ordonne l affichage des champs
        fields = ['nom', 
                  'description', 
                  'couleur', 
                  'ouvert',
                  'ouvert_mineur', 
                  'benevole', 
                  'planning', 
                  'equipe', 
                  'evenement']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # cache certains champs
        self.fields['planning'].widget = HiddenInput()
        self.fields['equipe'].widget = HiddenInput()
        self.fields['benevole'].widget = HiddenInput()
        self.fields['evenement'].widget = HiddenInput()


################################################################################################
class CreneauForm(ModelForm):
    debut = DateTimeField(widget=SplitDateTimeMultiWidget())
    fin = DateTimeField(widget=SplitDateTimeMultiWidget())
    benevole = ModelChoiceField(queryset=None,
                                required=False,
                                empty_label="Libre")
    class Meta:
        model = Creneau
        # exclude = ['benevole',]
        fields = ['debut',
                  'fin',
                  'benevole',
                  'description',
                  'editable',
                  'valide_present',
                  'type',
                  'poste',
                  'planning',
                  'equipe',
                  'evenement',
                  ]

    ################ methode __init__
    # surcharge les definition précédente de la class et permet de gerer les champs
    def __init__(self, *args, **kwargs):
        try:
            self.planning_uuid = kwargs.pop('planning_uuid')
        except:
            pass # on a deja le planning dans l'objet
        try:
            self.pas_creneau = kwargs.pop('pas_creneau')
        except:
            self.pas_creneau = 30
        try:
            self.poste_uuid = kwargs.pop('poste_uuid')
        except:
            pass
        try:
            self.benevole_uuid = kwargs.pop('benevole_uuid')
        except:
            self.benevole_uuid = ""
        try:
            self.type = kwargs.pop('type')
        except:
            pass
        try:
            self.personne_connectee = kwargs.pop('personne_connectee')
        except:
            pass
        try:
            self.evenement = kwargs.pop('evenement')
        except:
            pass

        super().__init__(*args, **kwargs)

        # les bénévoles actif et inscrit sur l evenement
        self.querysetbenevoles = ProfileBenevole.objects.filter(personne__is_active='1', BenevolesEvenement=self.evenement).order_by('personne__last_name', 'personne__first_name') 

        # cache certains champs
        self.fields['poste'].widget = HiddenInput()
        self.fields['planning'].widget = HiddenInput()
        self.fields['equipe'].widget = HiddenInput()
        self.fields['evenement'].widget = HiddenInput()
        self.fields['type'].widget = HiddenInput()
        # pas encore codé, on cache le champs
        self.fields['editable'].widget = HiddenInput()

        # recuperer le pas du planning associé
        # time_attr.step :  valeurs valides liées au pas du planning dans les choix en unités secondes :
        # ex 30 * 60 = 1800 : toutes les 30 minutes sont OK
        for trig in ('debut', 'fin'):
            self.fields[trig].widget = \
                SplitDateTimeMultiWidget(attrs={
                                                'date_attrs': {},
                                                'time_attrs': {'step': (self.pas_creneau * 60).__str__()}
                                                })

        # formulaire ayant une instance, on va travailler dessus pour afficher le fomulaire comme il faut
        # en fonction du profile utilisateur
        #instance = getattr(self, 'instance', None)
        # print(self.instance.UUID)
        # print('benevole : {}'.format(self.personne_connectee))
        if self.instance:
            if not self.personne_connectee:
                pass
            # la personne connectée est un pur bénévole
            if hasattr(self.personne_connectee, 'profilebenevole') and not self.personne_connectee.has_perm('evenement.change_creneau'):
                # par default, la liste de bénévole contient le benevole connecté
                id_benevole = self.personne_connectee.profilebenevole.UUID
                
                # OLD
                #for Creno in Creneau.objects.filter(Q(type="creneau"), Q(evenement_id=self.evenement), Q(benevole_id=id_benevole)):
                #    if self.instance.debut and self.instance.fin:
                #        #  l'instance est sur l'horaire du creneau de la liste
                #        if Creno.debut <= self.instance.debut < Creno.fin or Creno.debut < self.instance.fin <= Creno.fin \
                #            or self.instance.debut < Creno.debut < Creno.fin < self.instance.fin:
                #                # le benevole est pris sur l'intervale
                #                id_benevole = None

                if self.instance.debut and self.instance.fin:
                    # si on trouve un creneau sur la meme plage horaire ou le benevole est pris, alors on retire le benevole de la liste
                    for Creno in Creneau.objects.filter(Q(type="creneau"), 
                                                        Q(evenement_id=self.evenement), 
                                                        Q(benevole_id=id_benevole),
                                                        Q(debut__lte=self.instance.debut)&Q(fin__gt=self.instance.debut)|
                                                        Q(debut__lt=self.instance.fin)&Q(fin__gte=self.instance.fin)|
                                                        Q(debut__gt=self.instance.debut)&Q(fin__lt=self.instance.fin)&Q(debut__lt=F('fin')),
                                                        ):
                        id_benevole = None

                self.fields['benevole'].queryset = self.querysetbenevoles.filter(UUID=id_benevole)

            # la personne connectée est un responsbale/orga/admin
            elif self.personne_connectee.has_perm('evenement.change_creneau'): 
                # creneau disponible, on affiche tout la liste des bénévoles
                self.fields['benevole'].queryset = self.querysetbenevoles
                liste_benevoles_occupes = []

                # OLD
                #for Creno in Creneau.objects.filter(Q(type="creneau"), Q(evenement_id=self.evenement)):
                #    # si un bénévole est déjà pris sur l'horaire, on le sort de la liste
                #    if self.instance.debut and self.instance.fin:
                #        if Creno.debut <= self.instance.debut < Creno.fin or Creno.debut < self.instance.fin <= Creno.fin \
                #            or self.instance.debut < Creno.debut < Creno.fin < self.instance.fin and Creno.benevole_id:
                #            # on n'exclue pas le bénévole lié à l'objet, pour qu'il soit le choix par defaut dans la liste
                #            if Creno.UUID != self.instance.UUID:
                #                liste_benevoles_occupes.append(Creno.benevole_id)
                
                if self.instance.debut and self.instance.fin:
                    # on prend tous les creneaux sur la plage horaire avec un bénévole inscrit 
                    for Creno in Creneau.objects.filter(Q(type="creneau"), 
                                                        Q(evenement_id=self.evenement),
                                                        Q(debut__lte=self.instance.debut)&Q(fin__gt=self.instance.debut)|
                                                        Q(debut__lt=self.instance.fin)&Q(fin__gte=self.instance.fin)|
                                                        Q(debut__gt=self.instance.debut)&Q(debut__lt=self.instance.fin)&Q(debut__lt=F('fin')),
                                                        ).exclude(benevole_id=None):
                        # si un bénévole est déjà pris sur l'horaire, on le sort de la liste
                        if Creno.UUID != self.instance.UUID:
                            liste_benevoles_occupes.append(Creno.benevole_id)
                self.fields['benevole'].queryset = self.querysetbenevoles.select_related('personne').exclude(UUID__in=liste_benevoles_occupes)

    ################ methode controle_coherence_creneaux
    def controle_coherence_creneaux(self, Creno, debut, fin):
        # print(' ======== ')
        # print('ce creneau    : {}'.format(self.instance.UUID))
        uuid_autre_crenofield = Creno._meta.get_field('UUID')
        uuid_autre_creno = uuid_autre_crenofield.value_from_object(Creno)
        # print('autre creneau    : {}'.format(uuid_autre_creno))
        if self.instance.UUID != uuid_autre_creno:  # ne prend pas en compte l'instance en cours
            debut_autre_creno = Creno._meta.get_field('debut').value_from_object(Creno)
            fin_autre_creno = Creno._meta.get_field('fin').value_from_object(Creno)
            # print('autre creneau : {}'.format( Creno._meta.get_field('UUID').value_from_object(Creno)))
            # print ('autre debut  : {0}  fin : {1}'.format(debut_autre_creno, fin_autre_creno))
            # print('debut    : {}'.format(debut))
            if debut_autre_creno <= debut < fin_autre_creno:
                raise ValidationError("Wopolo le créneau commence sur un autre!")
            if debut_autre_creno < fin < fin_autre_creno:
                raise ValidationError("Wopolo le créneau fini sur un autre!")

    ################ methode clean
    # on valide les données pour avoir de la cohérence
    def clean(self):
        super().clean()
        debut = self.cleaned_data['debut']
        fin = self.cleaned_data['fin']
        Plan = Planning.objects.get(UUID=self.planning_uuid)
        planning_debut = Plan._meta.get_field('debut')
        planning_fin = Plan._meta.get_field('fin')
        # cohérence avec le planning
        if debut < planning_debut.value_from_object(Plan):
            raise ValidationError("Wopolo le créneau ne peut pas commencer avant le début du planning!")
        if fin > planning_fin.value_from_object(Plan):
            raise ValidationError("Wopolo le créneau ne peut pas finir après la fin du planning!")
        if debut >= fin:
            raise ValidationError("Wopolo la fin du créneau c'est après son début!")
        # cohérence avec les autre créneaux du poste sur le planning
        if self.poste_uuid and self.type=="creneau":
            for Creno in Creneau.objects.filter(planning=self.planning_uuid,
                                                poste=self.poste_uuid,
                                                type="creneau"):
                self.controle_coherence_creneaux(Creno, debut, fin)
        # cohérence avec les autre créneaux du benevole sur le planning 
        if self.benevole_uuid and self.type=="benevole":
            for Creno in Creneau.objects.filter(planning=self.planning_uuid,
                                                benevole=self.benevole_uuid,
                                                type="benevole"):
                self.controle_coherence_creneaux(Creno, debut, fin)
        # cohérence : le benevole ne peut pas s'inscrire sur deux créneaux aux meme heures
        if self.benevole_uuid and self.type=="creneau":
            for Creno in Creneau.objects.filter(benevole=self.benevole_uuid,
                                                type="creneau"):
                self.controle_coherence_creneaux(Creno, debut, fin)                                
        # pas de créneau type benevole sans benevole associé
        if self.type == "benevole" and self.benevole_uuid == "":
            raise ValidationError("Wopolo une dispo benevole sans benevole associé!")
