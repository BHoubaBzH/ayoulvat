from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from benevole.views import InscriptionView

urlpatterns = [
    # home page pour l'instant
    path('', TemplateView.as_view(template_name='benevole/home.html'), name='home'),
    # pages de login / logout ...
    path('', include('django.contrib.auth.urls')),
    path('inscription/', InscriptionView.as_view(), name='inscription'),
]
