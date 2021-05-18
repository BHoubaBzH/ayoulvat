import ordering as ordering
from django.contrib import admin

from .models import Formule
from modeltranslation.admin import TranslationAdmin

#class FormulesListe(admin.ModelAdmin):
class FormulesListe(TranslationAdmin):
    # partie édition
    fieldsets = [
        ('Nom', {'fields': ['nom']}),
        ('Coût', {'fields': ['cout']}),
        ('Details', {'fields': ['description']}),
    ]
    # partie affichage des formules
    list_display = ['nom', 'cout', 'description', 'UUID']
    # range par defaut par cout croissant a l'affichage

    class Meta:
        verbose_name = "options d'abonnement"

    def get_ordering(self, request):
        return ['cout']


admin.site.register(Formule, FormulesListe)
