import ordering as ordering
from django.contrib import admin

from .models import Formule


class FormulesListe(admin.ModelAdmin):
    # partie édition
    fieldsets = [
        ('Nom', {'fields': ['nom']}),
        ('Coût', {'fields': ['cout']}),
        ('Details', {'fields': ['description']}),
    ]
    # partie affichage des formules
    list_display = ['nom', 'cout', 'description', 'UUID_formule']
    # range par defaut par cout croissant a l'affichage

    class Meta:
        verbose_name = "options d'abonnement"

    def get_ordering(self, request):
        return ['cout']


admin.site.register(Formule, FormulesListe)
