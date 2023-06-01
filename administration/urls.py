from django.urls import path
from . import views

urlpatterns = [
    path('benevoles', views.BenevolesListView.as_view(), name='benevoles_liste'),
    path('creneaux', views.CreneauxListView.as_view(), name='creneaux_liste'),
    path('dashboard', views.DashboardView.as_view(), name='dashboard'),
    path('organization', views.OrganizationView.as_view(), name='organization'),
]
