from django.urls import path

from . import views

urlpatterns = [
    path('', views.liste_evenements, name='liste_evenements'),
    #path('equipe/', views.liste_equipes, name='liste_equipes'),
    #path('equipe/planning/', views.liste_plannings, name='liste_plannings'),
    #path('equipe/planning/poste/', views.liste_postes, name='liste_postes'),
    #path('equipe/planning/poste/creneau/', views.liste_creneaux, name='liste_creneaux'),

    #path('equipe/planning/poste/creneau/<uuid_creneau>/', views.detail_creneau, name='detail_creneau'),
    #path('equipe/planning/poste/<uuid_poste>/', views.detail_poste, name='detail_poste'),
    #path('equipe/planning/<uuid_planning>/', views.detail_planning, name='detail_planning'),
    #path('equipe/<uuid_equipe>/', views.detail_equipe, name='detail_equipe'),
    path('<uuid_evenement>/', views.detail_evenement, name='detail_evenement'),

]