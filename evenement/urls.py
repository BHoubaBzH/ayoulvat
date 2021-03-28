from django.urls import path

from . import views

urlpatterns = [
    path('', views.liste_evenements, name='liste_evenements'),
    path('<uuid_evenement>/', views.detail_evenement, name='detail_evenement'),

]