from uuid import UUID
from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from benevole.models import ProfileBenevole, Personne, ProfileOrganisateur

from evenement import models
from benevole import models as models_benevoles

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
        print(self.queryset.query)

class BenevoleEvenementInLine(admin.TabularInline):
    # table evenement_benevole_assopart
    verbose_name = 'bénévole événement'
    model = models.Evenement.benevole.through 
    formset = BenevoleEvenementFormSet
    extra = 0

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
    #filter_horizontal = ('benevole', 'assopartenaire')
    inlines = (BenevoleEvenementInLine, )

admin.site.register(models.Equipe)
admin.site.register(models.Planning)
admin.site.register(models.Poste)
