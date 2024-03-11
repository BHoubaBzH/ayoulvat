from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from benevole import models
from association import models as models_a
from evenement.admin import OrganisateurEvenementInLine, ResponsableEquipeInLine, BenevoleEvenementInLine 

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

########### FORMSETS ###########

class AdministrateurAssociationFormSet(BaseInlineFormSet):
    ''' admin asso '''
    def __init__(self, *args, **kwargs):
        super(AdministrateurAssociationFormSet, self).__init__(*args, **kwargs)
        self.queryset = self.queryset.select_related('profileadministrateur__personne', 'association')

class OrganisateurPersonneFormSet(BaseInlineFormSet):
    ''' organisateur evenement '''
    def __init__(self, *args, **kwargs):
        super(OrganisateurPersonneFormSet, self).__init__(*args, **kwargs)
        self.queryset = self.queryset.select_related('profileorganisateur__personne', 'evenement')

class BenevolePersonneFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(BenevolePersonneFormSet, self).__init__(*args, **kwargs)
        self.queryset = self.queryset.select_related('profilebenevole__personne', 'evenement', 'profilebenevole', 'asso_part')
        #print(self.queryset.query)

########### INLINES ###########

class AdministrateurAssociationInLine(admin.TabularInline):
    verbose_name = 'administrateur association'
    model = models_a.Association.administrateur.through
    formset = AdministrateurAssociationFormSet
    extra = 0
    raw_id_fields = ('association', ) 

class BenevolePersonneInLine(admin.TabularInline):
    verbose_name = 'bénévole événement'
    model = models.Personne
    formset = BenevolePersonneFormSet
    extra = 0
    raw_id_fields = ('profilebenevole', 'asso_part') # pas de selection directe dans la liste = divise le nombre de requete db par 8

########### TYPES USERS ###########

@admin.register(models.Personne)
class PersonneDetails(admin.ModelAdmin):
    def group(self, user):
        groups = []
        for group in user.groups.all():
            groups.append(group.name)
        return ' '.join(groups)
    group.short_description = 'Groupes'
    list_display = ( "email", "last_name", "first_name", "date_joined", "is_superuser", "group", "date_joined" )
    list_filter = ( "profilebenevole__evenement_benevole_assopart__evenement", 
                    "profilebenevole__evenement_benevole_assopart__evenement__association",
                    "groups", 
                    )
    ordering = ('last_name', 'first_name', 'email')
    # inlines = [BenevoleInLine, BenevolePersonneInLine], 

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
    list_display  = ('get_user_email', 'get_user_name', 'get_user_fisrtname')
    ordering = ('personne__last_name'.lower(), 'personne__first_name'.lower())

@admin.register(models.ProfileAdministrateur)
class AdministrateurCustom(BenevoleCommun):
    inlines = (AdministrateurAssociationInLine,)

@admin.register(models.ProfileOrganisateur)
class OrganisateurCustom(BenevoleCommun):
    inlines = (OrganisateurEvenementInLine,)

@admin.register(models.ProfileResponsable)
class ResponsableCustom(BenevoleCommun):
    inlines = (ResponsableEquipeInLine,)

@admin.register(models.ProfileBenevole)
class BenevoleCustom(BenevoleCommun):
    #def evenements(self, obj):
    #    return obj.evenement_benevole_assopart
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

#admin.site.unregister(User)
#admin.site.register(User, BenevoleDetails)

#admin.site.register(models.ProfileAdministrateur)
#admin.site.register(models_b.ProfileOrganisateur)
#admin.site.register(models_b.ProfileResponsable)
