from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from benevole import models

class PersonneInLine(admin.TabularInline):
    model = models.Personne
    can_delete = False
    verbose_name = 'Bénévoles'
    # fk_name = 'user'
    extra = 1


class BenevoleInLine(admin.TabularInline):
    model = models.ProfileBenevole
    can_delete = False
    verbose_name = 'Bénévoles'
    # fk_name = 'user'
    extra = 1

@admin.register(models.Personne)
class PersonneDetails(admin.ModelAdmin):
    def group(self, user):
        groups = []
        for group in user.groups.all():
            groups.append(group.name)
        return ' '.join(groups)
    # inlines = [BenevoleInLine, ]
    group.short_description = 'Groupes'
    list_display = ( "last_name", "first_name", "email", "date_joined", "is_superuser", "group")
    list_filter = ( "profilebenevole__evenement_benevole_assopart__evenement",
                    "profilebenevole__evenement_benevole_assopart",)

@admin.register(models.ProfileBenevole)
class BenevoleDetails(admin.ModelAdmin):
    #list_display = ( "ProfileBenevole_personne",)
    list_filter = ( "evenement_benevole_assopart__evenement",
                    "evenement_benevole_assopart",)
    # redefini le query set sur benevole pour y inclurer "personne" ->un join dans la requete sql
    # optimise les requetes 
    def get_queryset(self, request):
            qs = self.model._default_manager.select_related(
                'personne',
            )
            # This stuff is marked as TODO in Django 3.1
            # so it might change in the future
            ordering = self.get_ordering(request)
            if ordering:
                qs = qs.order_by(*ordering)
            return qs

#admin.site.unregister(User)
#admin.site.register(User, BenevoleDetails)

admin.site.register(models.ProfileAdministrateur)
admin.site.register(models.ProfileOrganisateur)
admin.site.register(models.ProfileResponsable)
