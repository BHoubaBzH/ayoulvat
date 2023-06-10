from django.contrib import admin

from .models import AssoPartenaire, Association, Abonnement
from benevole.models import *
from modeltranslation.admin import TranslationAdmin


class AbonnementInLine(admin.TabularInline):
    model = Abonnement
    extra = 0

class AssopartInline(admin.TabularInline):
    model = AssoPartenaire
    extra = 0

'''
class ProfileAdministrateurInLine(admin.TabularInline):
    model = ProfileAdministrateur
    can_delete = False
    verbose_name = 'Aministrateur'
    # fk_name = 'user'
    extra = 1
'''

#class AssociationDetails(admin.ModelAdmin):
class AssociationDetails(TranslationAdmin):
    # details affichés de l'asso dans la liste

    list_display = ['nom', 'description', 'courriel', ]
    inlines = [AbonnementInLine, AssopartInline]

class AssoPartenairesDetails(admin.ModelAdmin):
    def asso_nom(self):
        return Association.objects.get(UUID=self.Association_id).nom
    list_display = ['nom', asso_nom]

class AbonnementAdmin(admin.ModelAdmin):
    pass

admin.site.register(Association, AssociationDetails)
admin.site.register(Abonnement)
admin.site.register(AssoPartenaire, AssoPartenairesDetails)
# on Désenregistre le model User pour le replacer par le profile Administrateur
# admin.site.unregister(User)
# admin.site.register(User, AdministrateurDetails)

# admin.site.register(ProfileBenevole)
