from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from association.models import AssoPartenaire
from evenement import models


@admin.register(models.Creneau)
class CreneauAdmin(admin.ModelAdmin):
    list_display = ("nom", "benevole", "debut",  "type")
    list_filter = (
        "evenement", "benevole", "debut", 
    )

class BenevoleEvenementFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(BenevoleEvenementFormSet, self).__init__(*args, **kwargs)
        self.queryset = self.queryset.select_related('profilebenevole__personne', 'evenement', 'profilebenevole', 'asso_part')
        #print(self.queryset.query)

class BenevoleEvenementInLine(admin.TabularInline):
    # table evenement_benevole_assopart
    verbose_name = 'bénévole événement'
    model = models.Evenement.benevole.through 
    formset = BenevoleEvenementFormSet
    extra = 0
    raw_id_fields = ('profilebenevole', 'asso_part') # pas de selection directe dans la liste = divise le nombre de requete db par 8

#class AssopartInLine(admin.TabularInline):
#    model = AssoPartenaire
#    extra = 0

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
    #filter_horizontal = ('benevole', 'assopartenaire')
    list_select_related = ['association']
    inlines = (BenevoleEvenementInLine, )

    list_filter = ['association']

admin.site.register(models.Equipe)
admin.site.register(models.Planning)
admin.site.register(models.Poste)
