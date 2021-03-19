"""ayoulvat URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    # pages de login / logout ...
    # path('connect/', include('django.contrib.auth.urls')),
    # home page pour l'instant
    #path('', TemplateView.as_view(template_name='benevole/home.html'), name='home'),

    # conf finale
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('', include('django.contrib.auth.urls')),

    path('benevole/', include('benevole.urls')),
    path('association/', include('association.urls')),
    #path('registration/', TemplateView.as_view(template_name='registration/login.html'), name='login'),
]
