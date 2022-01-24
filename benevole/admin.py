from django.contrib import admin
from django.contrib.auth.models import User

from .models import Personne, ProfileAdministrateur, ProfileResponsable, ProfileOrganisateur, \
    ProfileBenevole
from django.contrib.auth.admin import UserAdmin

class PersonneInLine(admin.TabularInline):
    model = Personne
    can_delete = False
    verbose_name = 'Bénévoles'
    # fk_name = 'user'
    extra = 1

class PersonneDetails(admin.ModelAdmin):

    def group(self, user):
        groups = []
        for group in user.groups.all():
            groups.append(group.name)
        return ' '.join(groups)
    group.short_description = 'Groupes'
    list_display = ( "last_name", "first_name", "email", "date_joined", "is_superuser", "group")
    

'''
class BenevoleDetails(UserAdmin):
    inlines = [PersonneInLine, ]
    list_display = ('nom', )
    # va chercher last_name dans la class user liée par ManyToMany
    def last_name(self, obj):
        return obj.user.last_name
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(BenevoleDetails, self).get_inline_instances(request, obj)
'''


#admin.site.unregister(User)
#admin.site.register(User, BenevoleDetails)

admin.site.register(Personne, PersonneDetails)
admin.site.register(ProfileAdministrateur)
admin.site.register(ProfileOrganisateur)
admin.site.register(ProfileResponsable)
admin.site.register(ProfileBenevole)
