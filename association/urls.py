from django.urls import path

from . import views

urlpatterns = [
    path('', views.liste_assos, name='liste_assos'),
    path('<uuid_asso>/', views.detail_asso, name='detail_asso'),


]