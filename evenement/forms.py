from benevole.forms import PersonneForm
from administration.views import evenement
from uuid import UUID
from django.forms import ModelForm, DateTimeField, HiddenInput, ValidationError
from django.forms import ModelChoiceField, ModelMultipleChoiceField, CheckboxSelectMultiple
from django_range_slider.fields import RangeSliderField

from evenement.models import Equipe, Planning, Poste, Creneau
from benevole.models import ProfileBenevole
from evenement.customwidgets import SplitDateTimeMultiWidget


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
                  'evenement',]
                
    # cache certains champs
    def __init__(self, *args, **kwargs):
        super(EquipeForm, self).__init__(*args, **kwargs)
        # pas encore codé, on cache le champs
        self.fields['editable'].widget = HiddenInput()

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
                  'equipe',
                  'evenement',]

    # cache certains champs
    def __init__(self, *args, **kwargs):
        super(PlanningForm, self).__init__(*args, **kwargs)
        # pas encore codé, on cache le champs
        self.fields['editable'].widget = HiddenInput()
        self.fields['ouvert_mineur'].widget = HiddenInput()



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

    # cache certains champs
    def __init__(self, *args, **kwargs):
        super(PosteForm, self).__init__(*args, **kwargs)
        self.fields['planning'].widget = HiddenInput()
        self.fields['equipe'].widget = HiddenInput()
        self.fields['benevole'].widget = HiddenInput()
        self.fields['evenement'].widget = HiddenInput()


################################################################################################
class CreneauForm(ModelForm):
    QuerySet = ProfileBenevole.objects.filter(personne__is_active='1').order_by('personne__last_name')
    benevole = ModelChoiceField(queryset=QuerySet,
                                required=False,
                                empty_label="Libre")
    debut = DateTimeField(widget=SplitDateTimeMultiWidget())
    fin = DateTimeField(widget=SplitDateTimeMultiWidget())

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
                  'evenement',]

    ################ methode __init__
    # surcharge les definition précédente de la class et permet de gerer les champs
    def __init__(self, *args, **kwargs):
        self.pas_creneau = kwargs.pop('pas_creneau')
        self.planning_uuid = kwargs.pop('planning_uuid')

        try:
            self.poste_uuid = kwargs.pop('poste_uuid')
        except:
            pass
        try:
            self.benevole_uuid = kwargs.pop('benevole_uuid')
        except:
            # self.benevole_uuid = Creneau.objects.get(UUID=self.UUID)
            self.benevole_uuid = ""
        try:
            self.type = kwargs.pop('type')
        except:
            pass
        try:
            self.personne_connectee = kwargs.pop('personne_connectee')
        except:
            pass

        # si type = creneau et poste_uuid et benevole_uuid , creneau avec benevole affecté
        # si type = creneau et poste_uuid sans benevole_uuid, creneau disponible
        # si type = benevole et benevole_uuid, dispo du benevole
        super(CreneauForm, self).__init__(*args, **kwargs)
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
        instance = getattr(self, 'instance', None)
        # print('benevole asso : {}'.format(self.personne_connectee.assopartenaire_id))
        if instance:
            # la personne est aussi un benevole
            if hasattr(self.personne_connectee, 'profilebenevole'):
                liste_benevoles_inscrits = []
                # si non admin/responsable, le benevole n'a pas accès a ces champs
                if not self.personne_connectee.has_perm('evenement.change_creneau'):
                    for champs in self.fields:
                        self.fields[champs].widget.attrs['readonly'] = True
                    self.fields['editable'].widget = HiddenInput()
                # par default, la liste des benevoles présentée est : vide + le benevole connecté
                self.fields['benevole'].queryset = ProfileBenevole.objects.filter(UUID=self.personne_connectee.profilebenevole.UUID)
                # si on edite une proposition de dispo benevole ou si on en cree une,
                # on retire vide dans la liste benevoles et on permet de modifier les heures
                if self.instance.type == "benevole" or self.type == "benevole" or self.type is None:
                    # un admin cree un nouveau creneau affecté a personne par defaut
                    # du coup on ne force pas le bénévole initial
                    if not self.personne_connectee.has_perm('evenement.change_creneau'):
                        self.fields['benevole'].empty_label = None
                        self.fields['benevole'].initial = \
                            ProfileBenevole.objects.get(UUID=self.personne_connectee.profilebenevole.UUID)
                    self.fields['debut'].widget.attrs['readonly'] = False
                    self.fields['fin'].widget.attrs['readonly'] = False
                # si c'est un creneau affecté à un autre benevole, on affiche juste ce benevole
                elif self.instance.benevole_id != self.personne_connectee.profilebenevole.UUID and \
                        self.instance.benevole_id is not None and self.instance.benevole_id != "":
                    self.fields['benevole'].queryset = \
                        ProfileBenevole.objects.filter(UUID=self.instance.benevole_id)
                    # un admin peut enlever un benevole d un creneau, on ne lui retire pas vide de la liste des benevoles
                    if not self.personne_connectee.has_perm('evenement.change_creneau'):
                        self.fields['benevole'].empty_label = None
                # si le bénévole est aussi un admin, et que le créneau est libre
                # on propose a l admin la liste de tous les benevoles!!! attention , sur le benevole est deja sur un autre creneau à la meme heure ca ne fonctionne pas
                elif self.personne_connectee.has_perm('evenement.change_creneau') and self.instance.benevole_id is None :
                    self.fields['benevole'].queryset = self.QuerySet


                # si le bénévole est déjà positionné sur un Creno au meme heures que celui-ci, on ne lui propose pas de prendre celui-ci
                elif self.instance.benevole_id != self.personne_connectee.profilebenevole.UUID:
                    for Creno in Creneau.objects.filter(benevole_id=self.personne_connectee.profilebenevole.UUID, type="creneau"):
                        # si le debut ou la fin de l'instance est dans l'intervale d'un creneau affecté a ce bénévole, 
                        # ou si le benevole a deja un créneau affecté compris intégralement dans celui-ci
                        try:
                            self.instance.debut
                            if Creno.debut <= self.instance.debut < Creno.fin or Creno.debut < self.instance.fin <= Creno.fin \
                                or self.instance.debut < Creno.debut < Creno.fin < self.instance.fin:
                                self.fields['benevole'].queryset = ProfileBenevole.objects.filter(UUID=None)
                        except:
                            pass


            # orga, admin, responsable et pas benevole: on propose uniquement les bénévoles qui ont une
            # dispo sur le planning au heures qui vont bien et sur les plannning deja créés donc avec un self.instance.planning_id
            elif self.personne_connectee.has_perm('evenement.change_creneau'): # and self.instance.planning_id:
                liste_benevoles_inscrits = []
                # print('************************************************')
                # liste les benevoles ayant mis une dispo (Creno) englobant ce creneau
                try:
                    instance_planning = self.instance.planning_id
                except:
                    instance_planning = None
                if instance_planning:
                    for Creno in Creneau.objects.filter(planning_id=self.instance.planning_id, type="benevole"):
                        # si le creneau est dans l'interval d'une dispo alors on propose le benevole dispo
                        if Creno.debut <= self.instance.debut and self.instance.fin <= Creno.fin :
                            liste_benevoles_inscrits.append(Creno.benevole_id)
                        # print('liste benevole ayant mis une dispo sur cet intervale : {}'.format(liste_benevoles_inscrits))
                    # retraite la liste des benevole disponible, et si ils sont déjà inscrits sur un creneau
                    # au meme moment, on retire le bénévole de la liste sauf si c'est le bénévole du creneau actuel
                    for Creno in Creneau.objects.filter(benevole_id__in=liste_benevoles_inscrits, type="creneau"):
                        # si c'est le creneau ou le benevole est pris, on propose le benevole dans la liste, sinon
                        if str(self.instance.benevole_id) != str(Creno.benevole_id):
                            # si le debut ou la fin du creneau est dans l'intervale d'un creneau affecté au bénévole, 
                            # ou si le benevole a deja un créneau affecté compris intégralement dans celui-ci
                            if Creno.debut <= self.instance.debut < Creno.fin or Creno.debut < self.instance.fin <= Creno.fin \
                                or self.instance.debut < Creno.debut < Creno.fin < self.instance.fin:
                                # print('benevole ayant mis une dispo sur cet intervale et etant deja reservé sur un autre creneau : {}'.format(Creno.benevole_id))
                                try:
                                    liste_benevoles_inscrits.remove(Creno.benevole_id)
                                except:
                                    pass
                else: # nouveau creneau
                    pass # les nouveau créneau sont créés sans bénévole (libre)
                
                # print('liste benevole proposée du coup : {}'.format(liste_benevoles_inscrits))
                self.fields['benevole'].queryset = ProfileBenevole.objects.filter(UUID__in=liste_benevoles_inscrits)

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

