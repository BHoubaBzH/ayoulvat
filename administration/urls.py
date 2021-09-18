from django.urls import path
from . import views

urlpatterns = [
    #path('benevole/ajoute', views.benevole_ajoute, name='benevole_ajoute'),
    #path('benevole/edite', views.benevole_edite, name='benevole_edite'),
    #path('benevole/supprime', views.benevole_supprime, name='benevole_supprime'),
    #path('benevoles', views.benevoles_liste, name='benevoles_liste'),
    path('benevoles', views.BenevolesListView.as_view(), name='benevoles_liste'),
]
