from django.urls import path

from . import views

urlpatterns = [
    # test phil premiere page
    path('', views.ShowAsso, name='show_asso'),


]