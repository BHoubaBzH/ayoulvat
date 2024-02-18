from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from association.models import AssoPartenaire
from evenement import models

#class AssopartInLine(admin.TabularInline):
#    model = AssoPartenaire
#    extra = 0

########### FORMSETS ###########

class OrganisateurEvenementFormSet(BaseInlineFormSet):
    ''' organisateur evenement '''
    def __init__(self, *args, **kwargs):
        super(OrganisateurEvenementFormSet, self).__init__(*args, **kwargs)
        self.queryset = self.queryset.select_related('profileorganisateur__personne', 'evenement')

class ResponsableEquipeFormSet(BaseInlineFormSet):
    ''' responsable equipe '''
    def __init__(self, *args, **kwargs):
        super(ResponsableEquipeFormSet, self).__init__(*args, **kwargs)
        self.queryset = self.queryset.select_related('profileresponsable__personne', 'equipe')

class BenevoleEvenementFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(BenevoleEvenementFormSet, self).__init__(*args, **kwargs)
        self.queryset = self.queryset.select_related('profilebenevole__personne', 'evenement', 'profilebenevole', 'asso_part')
        #print(self.queryset.query)

########### INLINES ###########

class OrganisateurEvenementInLine(admin.TabularInline):
    # table evenement_benevole_assopart
    verbose_name = 'organisateur événement'
    model = models.Evenement.organisateur.through 
    formset = OrganisateurEvenementFormSet
    extra = 0
    raw_id_fields = ('evenement', ) # pas de selection directe dans la liste = divise le nombre de requete db par 8

class ResponsableEquipeInLine(admin.TabularInline):
    # table evenement_benevole_assopart
    verbose_name = 'organisateur événement'
    model = models.Equipe.responsable.through 
    formset = ResponsableEquipeFormSet
    extra = 0
    raw_id_fields = ('equipe', ) # pas de selection directe dans la liste = divise le nombre de requete db par 8    

class BenevoleEvenementInLine(admin.TabularInline):
    verbose_name = 'bénévole événement'
    model = models.Evenement.benevole.through 
    formset = BenevoleEvenementFormSet
    extra = 0
    raw_id_fields = ('profilebenevole', 'asso_part') # pas de selection directe dans la liste = divise le nombre de requete db par 8

class AssopartInline(admin.TabularInline):
    model = AssoPartenaire
    extra = 0

    def get_form_queryset(self, obj):
        return self.model.objects.filter(Association=obj.association)

###########  ###########

@admin.register(models.Evenement)
class EvenementAdmin(admin.ModelAdmin):
    list_display = ("nom", "debut", "fin", "inscription_debut", "inscription_fin")
    fieldsets = (
                    ('Général', { 'fields': (
                                    ('nom', 'association', 'organisateur', 'editable'),
                                    'site_web', 
                                    'description', 
                                    'vignette', 
                                    'couleur',
                                    'courriel_organisateur',
                                )
                                }),
                    ('Details', { 'fields': (
                                    ('debut', 'fin'), 
                                    ('inscription_debut', 'inscription_fin'), 
                                    #('benevole', 'assopartenaire')),
                                    'assopartenaire', 'commentaire',
                                ),
                    # affichage
                    'classes': ('wide', 'extrapretty'),
                                }),
                )
    filter_horizontal = ('organisateur', 'assopartenaire', )
    # inlines = [AssopartInline]
    # filter_horizontal = ('benevole', 'assopartenaire')
    # list_select_related = ['association', ]

    # liste de benevole trop lourd pour édition, retiré
    # inlines = (BenevoleEvenementInLine, )

    list_filter = ['association']
    

@admin.register(models.Equipe)
class EquipeAdmin(admin.ModelAdmin):
    list_display = ("nom", "evenement" )
    list_filter = ['evenement', ]

@admin.register(models.Planning)
class PlanningAdmin(admin.ModelAdmin):
    list_display = ("nom", "equipe", "evenement" )
    list_filter = ['evenement', 'equipe']

@admin.register(models.Poste)
class PosteAdmin(admin.ModelAdmin):
    list_display = ("nom", "equipe", "evenement", "planning" )
    list_filter = ['evenement', 'equipe', 'planning']

@admin.register(models.Creneau)
class CreneauAdmin(admin.ModelAdmin):
    list_display = ("nom", "benevole", "debut",  "type")
    list_filter = ["evenement", "benevole", "debut"]