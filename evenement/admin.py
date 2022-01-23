from django.contrib import admin

from evenement.models import *

@admin.register(Creneau)
class CreneauAdmin(admin.ModelAdmin):
    list_display = ("nom", "debut", "benevole", "type")
    list_filter = (
        "benevole", "debut", 
    )

@admin.register(Evenement)
class EvenementAdmin(admin.ModelAdmin):
    list_display = ("nom", "debut", "fin", "inscription_debut", "inscription_fin")

    fieldsets = (
        (None, {
            'fields': (('nom', 'association', 'organisateur', 'editable'), 
                        ('debut', 'fin'), 
                        ('inscription_debut', 'inscription_fin'), 
                        'courriel_responsable', 'site_web', 'description', 'vignette', 'couleur',
                        ('benevole', 'assopartenaire')),
            # affichage
            'classes': ('wide', 'extrapretty'),
        }),
    )


#admin.site.register(Evenement)
admin.site.register(Equipe)
admin.site.register(Planning)
#admin.site.register(Creneau)
admin.site.register(Poste)
