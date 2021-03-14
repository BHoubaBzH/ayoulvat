from django.contrib import admin
from django.contrib.auth.models import User

from .models import ProfileBenevole, Origine


# admin.site.unregister(User)
admin.site.register(ProfileBenevole)
admin.site.register(Origine)
