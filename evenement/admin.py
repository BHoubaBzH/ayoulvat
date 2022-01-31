from django.contrib import admin
from administration.views import evenement

from evenement.models import *

@admin.register(Creneau)
class CreneauAdmin(admin.ModelAdmin):
    list_display = ("nom", "debut", "benevole", "type")
    list_filter = (
        "benevole", "debut", 
    )

class BenevoleInlineEvenement(admin.TabularInline):
    # table evenement_benevole_assopart
    model = Evenement.benevole.through
    extra = 0
@admin.register(Evenement)
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
    inlines = (BenevoleInlineEvenement,)

#admin.site.register(Evenement)
admin.site.register(Equipe)
admin.site.register(Planning)
#admin.site.register(Creneau)
admin.site.register(Poste)
