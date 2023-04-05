from django.contrib import admin
from benevole import models
from evenement.admin import BenevoleEvenementInLine


class PersonneInLine(admin.TabularInline):
    model = models.Personne
    can_delete = False
    verbose_name = 'Personne'
    extra = 1

class BenevoleInLine(admin.TabularInline):
    model = models.ProfileBenevole
    can_delete = False
    verbose_name = 'Bénévoles'
    #fk_name = 'personne'
    extra = 1
    #fieldsets = (
    #    (None, {
    #        'fields': ('message', 'UUID ')
    #    }),
    #    ('Advanced options', {
    #        'classes': ('collapse',),
    #        'fields': ('message', ),
    #    }),
    #)

@admin.register(models.Personne)
class PersonneDetails(admin.ModelAdmin):
    def group(self, user):
        groups = []
        for group in user.groups.all():
            groups.append(group.name)
        return ' '.join(groups)
    #inlines = [BenevoleInLine, ]
    group.short_description = 'Groupes'
    list_display = ( "email", "last_name", "first_name", "date_joined", "is_superuser", "group")
    list_filter = ( "profilebenevole__evenement_benevole_assopart__evenement", 
                    "profilebenevole__evenement_benevole_assopart__evenement__association",
                    "groups", 
                    )

class BenevoleCommun(admin.ModelAdmin):
    """
        class héritée pour l'affichage commun des infos du bénévole 
    """
    def get_user_name(self, obj):
        return obj.personne.last_name
    def get_user_fisrtname(self, obj):
        return obj.personne.first_name
    def get_user_email(self, obj):
        return obj.personne.email
    get_user_name.short_description = 'Nom'
    get_user_fisrtname.short_description = 'Prénom'
    get_user_email.short_description = 'Courriel'
    get_user_name.admin_order_field = 'personne__last_name'

@admin.register(models.ProfileBenevole)
class BenevoleCustom(BenevoleCommun):
    #def evenements(self, obj):
    #    return obj.evenement_benevole_assopart
    list_display = ('get_user_email', 'get_user_name', 'get_user_fisrtname')

    list_filter = ( "evenement_benevole_assopart__evenement",
                )

    # redefini le query set sur benevole pour y inclurer "personne" ->un join dans la requete sql
    # optimise les requetes 
    def get_queryset(self, request):
            qs = self.model._default_manager.select_related(
                'personne',
            )
            ordering = self.get_ordering(request)
            if ordering:
                qs = qs.order_by(*ordering)
            return qs
    inlines = (BenevoleEvenementInLine,)

@admin.register(models.ProfileAdministrateur)
class AdministrateurCustom(BenevoleCommun):
    def assos(self, obj):
        return obj.association
    list_display  = ('get_user_email', 'get_user_name', 'get_user_fisrtname', 'assos')

@admin.register(models.ProfileOrganisateur)
class OrganisateurCustom(BenevoleCommun):
    list_display  = ('get_user_email', 'get_user_name', 'get_user_fisrtname')

@admin.register(models.ProfileResponsable)
class ResponsableCustom(BenevoleCommun):
    list_display  = ('get_user_email', 'get_user_name', 'get_user_fisrtname')


#admin.site.unregister(User)
#admin.site.register(User, BenevoleDetails)

#admin.site.register(models.ProfileAdministrateur)
#admin.site.register(models.ProfileOrganisateur)
#admin.site.register(models.ProfileResponsable)
