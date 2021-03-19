from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from benevole.views import InscriptionView

urlpatterns = [
    path('inscription/', InscriptionView.as_view(), name='inscription'),
]
