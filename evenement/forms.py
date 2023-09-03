from ast import Eq
from curses.ascii import CR
from datetime import datetime
from django.db import connection

from django.forms import DateField, DateInput, DateTimeInput, ModelForm, DateTimeField, HiddenInput, SelectDateWidget, ValidationError
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
class EvenementForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['association'].widget         = HiddenInput()
        self.fields['benevole'].widget            = HiddenInput()

        self.fields['debut'].widget               = SplitDateTimeMultiWidget(
                                                        attrs={
                                                            'time_attrs' : {'value' : '00:00',},
                                                        })
        self.fields['fin'].widget                 = SplitDateTimeMultiWidget(
                                                        attrs={
                                                            'time_attrs' : {'value' : '00:00',},
                                                        })

        self.fields['inscription_debut'].widget   = DateInput(
            attrs={
                'type': 'date', 
                }
        )
        self.fields['inscription_fin'].widget   = DateInput(
            attrs={
                'type': 'date', 
                }
        )

    class Meta:
        model = Evenement
        fields = '__all__'

    ################ methode clean
    # on valide les données pour avoir de la cohérence
    def clean(self):
        super().clean()
        debut = self.cleaned_data['debut']
        fin = self.cleaned_data['fin']
        inscription_debut = self.cleaned_data['inscription_debut']
        inscription_fin = self.cleaned_data['inscription_fin']
        
        if debut > fin :
            raise ValidationError("La fin de l\'évènement ne peut pas être avant le début")
        if debut < datetime.today():
            raise ValidationError("le nouvel évènement ne peut pas être dans le passé")
        if inscription_debut > inscription_fin :
            raise ValidationError("La fin des inscriptions ne peut pas être avant le début")
        if inscription_fin > fin.date() :
            raise ValidationError("La fin des inscriptions ne peut pas être après l\'évènement")
    
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
                  'evenement', # test pour la creation de equipe et sans accès à ce champs
                  ]
                
    # cache certains champs
    def __init__(self, *args, **kwargs):
        logger.debug(f'kwargs: {kwargs}')
        if initial := kwargs.get('initial', {}):
            self.evenements = initial['evenement']
        super().__init__(*args, **kwargs)
        # pas encore codé, on cache le champs
        self.fields['editable'].widget            = HiddenInput()
        self.fields['evenement'].widget           = HiddenInput()
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
        
    ################ methode __init__
    # surcharge les definition précédente de la class et permet de gerer les champs
    def __init__(self, *args, **kwargs):
        logger.debug(f'kwargs: {kwargs}')
        if initial := kwargs.get('initial', {}):
            self.equipe     = initial['equipe']
            self.evenements = initial['evenement']

        super().__init__(*args, **kwargs)
        # pas encore codé, on cache le champs
        self.fields['editable'].widget            = HiddenInput()
        self.fields['ouvert_mineur'].widget       = HiddenInput()
        self.fields['equipe'].widget              = HiddenInput()
        self.fields['evenement'].widget           = HiddenInput()
        self.fields['seuil1'].widget.attrs['min'] = '0'
        self.fields['seuil1'].widget.attrs['max'] = '100'
        self.fields['seuil2'].widget.attrs['min'] = '0'
        self.fields['seuil2'].widget.attrs['max'] = '100'

    ################ methode clean
    # on valide les données pour avoir de la cohérence
    def clean(self):
        super().clean()
        debut = self.cleaned_data['debut']
        fin = self.cleaned_data['fin']
        equipe = self.cleaned_data['equipe']
        event = self.cleaned_data['evenement']

        uuid = self.instance.UUID
        #    si debut planning est avant debut evenement ou apres fin evenement ou
        #    si fin planning est avant debut evenement ou apres fin evenement
        if debut < event.debut  or event.fin < debut or \
            fin < event.debut  or event.fin < fin :
            raise ValidationError("Le planning doit être dans l'évènement")
        #    si debut self est entre debut et fin autres planning equipe 
        #    si fin self est entre debut et fin autres planning equipe
        #    si self contient un autre planning
        #    si self est contenu dans un autre planning
        plans = Planning.objects.filter(equipe_id=equipe)
        for plan in plans:
            if  uuid != plan.UUID:
                # le planning de la liste n est pas self
                if plan.debut <= debut < plan.fin or \
                    plan.debut < fin <= plan.fin or \
                    debut <= plan.debut and plan.fin <= fin or \
                    plan.debut <= debut and fin <= plan.fin :
                    raise ValidationError("Le planning ne peut pas chevaucher un autre planning de la même équipe")
        #   si debut self est apres fin self
        if fin <= debut:
            raise ValidationError("mais tu es un grand malade toi!")
        # ou si encore des creneaux dedans
        # ou si debut self est apres debut d'un des creneaux du planning
        # ou si fin self est avant la fin d'un des creneaux du planning
        for cren in Creneau.objects.filter(planning_id=self.instance.UUID):
            if debut > cren.debut:
                raise ValidationError("impossible: au moins un creneau du planning commence avant.")
            if fin < cren.fin:
                raise ValidationError("impossible: au moins un creneau du planning fini plus tard.")


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
        logger.debug(f'kwargs: {kwargs}')
        if initial := kwargs.get('initial', {}):
            self.equipe     = initial['equipe']
            self.evenements = initial['evenement']
        super().__init__(*args, **kwargs)
        # cache certains champs
        self.fields['planning'].widget  = HiddenInput()
        self.fields['equipe'].widget    = HiddenInput()
        self.fields['benevole'].widget  = HiddenInput()
        self.fields['evenement'].widget = HiddenInput()


################################################################################################
class CreneauForm(ModelForm):
    """ 
        form creneau générique
    """
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
            self.personne_connectee_roles = kwargs.pop('personne_connectee_roles')
        except:
            self.personne_connectee_roles = ""
        try:
            self.evenement = kwargs.pop('evenement')
        except:
            pass
        super().__init__(*args, **kwargs)

        # les bénévoles actif et inscrit sur l evenement
        self.querysetbenevoles = ProfileBenevole.objects.filter(personne__is_active='1', BenevolesEvenement=self.evenement).order_by('personne__last_name', 'personne__first_name').select_related('personne')
        # cache certains champs
        self.fields['poste'].widget     = HiddenInput()
        self.fields['planning'].widget  = HiddenInput()
        self.fields['equipe'].widget    = HiddenInput()
        self.fields['evenement'].widget = HiddenInput()
        self.fields['type'].widget      = HiddenInput()
        # pas encore codé, on cache le champs
        self.fields['editable'].widget  = HiddenInput()

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
            # la personne connectée est uniquement bénévole
            if 'Benevole' in self.personne_connectee_roles \
                and not any(item in ('Administrateur', 'Organisateur', 'Responsable') for item in self.personne_connectee_roles):
            #if hasattr(self.personne_connectee, 'profilebenevole') and not self.personne_connectee.has_perm('evenement.change_creneau'):
                # par default, la liste de bénévole contient le benevole connecté
                id_benevole = self.personne_connectee.profilebenevole.UUID

                if self.instance.debut and self.instance.fin:
                    # si on trouve un creneau sur la meme plage horaire ou le benevole est pris, alors on retire le benevole de la liste
                    crenos = Creneau.objects.filter(Q(type="creneau"), 
                                                        Q(evenement_id=self.evenement), 
                                                        Q(benevole_id=id_benevole),
                                                        Q(debut__lte=self.instance.debut)&Q(fin__gt=self.instance.debut)|
                                                        Q(debut__lt=self.instance.fin)&Q(fin__gte=self.instance.fin)|
                                                        Q(debut__gt=self.instance.debut)&Q(fin__lt=self.instance.fin)&Q(debut__lt=F('fin'))
                                                        )
                    for Creno in crenos:
                        id_benevole = None

                self.fields['benevole'].queryset = self.querysetbenevoles.filter(UUID=id_benevole)

            # la personne connectée est un responsable/orga/admin
            elif any(item in ('Administrateur', 'Organisateur', 'Responsable') for item in self.personne_connectee_roles):
            #elif self.personne_connectee.has_perm('evenement.change_creneau'): 
                # creneau disponible, on affiche tout la liste des bénévoles
                self.fields['benevole'].queryset = self.querysetbenevoles
                liste_benevoles_occupes = []
                
                if self.instance.debut and self.instance.fin:
                    # on prend tous les creneaux sur la plage horaire avec un bénévole inscrit 
                    crenos = Creneau.objects.filter(Q(type="creneau"), 
                                                        Q(evenement_id=self.evenement),
                                                        Q(debut__lte=self.instance.debut)&Q(fin__gt=self.instance.debut)|
                                                        Q(debut__lt=self.instance.fin)&Q(fin__gte=self.instance.fin)|
                                                        Q(debut__gt=self.instance.debut)&Q(debut__lt=self.instance.fin)&Q(debut__lt=F('fin')),
                                                        ).exclude(benevole_id=None)
                    for Creno in crenos:
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
                raise ValidationError("le créneau commence sur un autre!")
            if debut_autre_creno < fin < fin_autre_creno:
                raise ValidationError("le créneau fini sur un autre!")

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
            raise ValidationError("le créneau ne peut pas commencer avant le début du planning!")
        if fin > planning_fin.value_from_object(Plan):
            raise ValidationError("le créneau ne peut pas finir après la fin du planning!")
        if debut >= fin:
            raise ValidationError("la fin du créneau doit être après son début!")
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
            raise ValidationError("une dispo benevole sans benevole associé!")
