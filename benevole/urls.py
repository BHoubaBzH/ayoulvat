from django import views
from django.urls import path

from benevole.views import InscriptionView
from . import views

urlpatterns = [
    path('inscription', InscriptionView.as_view(), name='inscription'),
    path('profile', views.Profile, name='profile'),
]

