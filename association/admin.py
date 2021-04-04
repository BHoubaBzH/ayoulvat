from django.contrib import admin

from .models import Association, Abonnement
# from benevole.models import ProfileBenevole


class AbonnementInLine(admin.TabularInline):
    model = Abonnement
    extra = 0

'''
class ProfileAdministrateurInLine(admin.TabularInline):
    model = ProfileBenevole
    can_delete = False
    verbose_name = 'Aministrateur'
    # fk_name = 'user'
    extra = 1
'''


class AssociationDetails(admin.ModelAdmin):
    # details affichés de l'asso dans la liste
    list_display = ['nom', 'description', 'courriel']
    inlines = [AbonnementInLine, ]


'''
class AdministrateurDetails(UserAdmin):
    inlines = [ProfileAdministrateurInLine, ]
    list_display = ('last_name', )
    # va chercher last_name dans la class user liée par ManyToMany
    def last_name(self, obj):
        return obj.user.last_name
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(AdministrateurDetails, self).get_inline_instances(request, obj)
'''


admin.site.register(Association, AssociationDetails)
admin.site.register(Abonnement)
# on Désenregistre le model User pour le replacer par le profile Administrateur
# admin.site.unregister(User)
# admin.site.register(User, AdministrateurDetails)

# admin.site.register(ProfileBenevole)

'''
######################################
# test de gestion user + profile dans la partie de l'admin
######################################
class ProfileAdministrateurAdmin(admin.ModelAdmin):
    readonly_fields = ['role']  # Be sure to read only mode
    fields = ('role', 'date_de_naissance')  # Specify the fields that need to be displayed in the administrative form
    list_display = ('last_name', 'first_name',)
    # va chercher last_name dans la class user liée par ManyToMany
    def last_name(self, obj):
        return obj.user.last_name.upper()
    def first_name(self, obj):
        return obj.user.first_name.capitalize()

class ProfileInline(admin.StackedInline):
    model = ProfileAdministrateur  # specify the profile model
    can_delete = False  # prohibit removal
    fields = ('last_name',)  # Specify which field to display,
    readonly_fields = ['last_name','first_name','role']  # Specify that this read only field


admin.site.register(ProfileAdministrateur, ProfileAdministrateurAdmin)

'''
