from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_evenements, name='liste_evenements'),
    path('<uuid:uuid_evenement>/', views.evenement, name='evenement'),
    path('creneau_fetch', views.CreneauFetch, name='creneau_fetch'),
    path('planning_fetch', views.PlanningFetch, name='planning_fetch'),
]
