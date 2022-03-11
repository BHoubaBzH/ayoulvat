from django.contrib import admin
from django.forms.models import BaseInlineFormSet

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
        self.queryset = self.queryset.select_related('evenement', 'profilebenevole', 'asso_part', 'profilebenevole__personne')

class BenevoleEvenementInLine(admin.TabularInline):
    # table evenement_benevole_assopart
    model = models.Evenement.benevole.through 
    formset = BenevoleEvenementFormSet
    extra = 0

    #def get_queryset(self, request):
    #        qs = self.model._default_manager.select_related(
    #            'evenement', 
    #            'profilebenevole__personne', 
    #            'asso_part', 
    #        )
    #        # This stuff is marked as TODO in Django 3.1
    #        # so it might change in the future
    #        ordering = self.get_ordering(request)
    #        if ordering:
    #            qs = qs.order_by(*ordering)
    #        return qs

@admin.register(models.Evenement)
class EvenementAdmin(admin.ModelAdmin):
    list_display = ("nom", "debut", "fin", "inscription_debut", "inscription_fin")
    fieldsets = (
        (None, {
            'fields': (('nom', 'association', 'organisateur', 'editable'), 
                        ('debut', 'fin'), 
                        ('inscription_debut', 'inscription_fin'), 
                        'courriel_organisateur', 'site_web', 'description', 'vignette', 'couleur',
                        #('benevole', 'assopartenaire')),
                        'assopartenaire'),
            # affichage
            'classes': ('wide', 'extrapretty'),
        }),
    )
    #filter_horizontal = ('benevole', 'assopartenaire')
    inlines = (BenevoleEvenementInLine,)

admin.site.register(models.Equipe)
admin.site.register(models.Planning)
admin.site.register(models.Poste)
