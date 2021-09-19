from django.urls import path
from . import views

urlpatterns = [
    path('benevoles', views.BenevolesListView.as_view(), name='benevoles_liste'),
    path('dashboard', views.DashboardView.as_view(), name='dashboard'),
]
