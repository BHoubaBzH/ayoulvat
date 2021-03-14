from django.contrib import admin
from django.contrib.auth.models import User

from .models import ProfileBenevole, Origine
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

class ProfileBenevoleInLine(admin.TabularInline):
    model = ProfileBenevole
    can_delete = False
    verbose_name = 'Bénévoles'
    # fk_name = 'user'
    extra = 1

class BenevoleDetails(UserAdmin):
    inlines = [ProfileBenevoleInLine, ]
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

admin.site.register(ProfileBenevole)
admin.site.register(Origine)
