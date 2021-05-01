from django.contrib import admin

from evenement.models import *

@admin.register(Creneau)
class CreneauAdmin(admin.ModelAdmin):
    list_display = ("nom", "benevole_id", "type")


admin.site.register(Evenement)
admin.site.register(Equipe)
admin.site.register(Planning)
#admin.site.register(Creneau)
admin.site.register(Poste)

