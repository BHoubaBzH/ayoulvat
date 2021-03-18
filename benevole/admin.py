from django.contrib import admin
from django.contrib.auth.models import User

from .models import ProfilePersonne, Origine, ProfileGestionnaire, ProfileResponsable, ProfileOrganisateur, \
    ProfileBenevole
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

class ProfilePersonneInLine(admin.TabularInline):
    model = ProfilePersonne
    can_delete = False
    verbose_name = 'Bénévoles'
    # fk_name = 'user'
    extra = 1

class BenevoleDetails(UserAdmin):
    inlines = [ProfilePersonneInLine, ]
    list_display = ('last_name', )
    # va chercher last_name dans la class user liée par ManyToMany
    def last_name(self, obj):
        return obj.user.last_name
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(BenevoleDetails, self).get_inline_instances(request, obj)


#admin.site.unregister(User)
#admin.site.register(User, BenevoleDetails)

admin.site.register(ProfilePersonne)
admin.site.register(ProfileGestionnaire)
admin.site.register(ProfileOrganisateur)
admin.site.register(ProfileResponsable)
admin.site.register(ProfileBenevole)
admin.site.register(Origine)
