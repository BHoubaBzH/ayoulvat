

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
from ayoulvat.settings import STATICFILES_DIRS
from benevole import views
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
# debug perfs
if settings.DEBUG:
    import debug_toolbar

urlpatterns = [
    path('admin/', admin.site.urls),

    #path('', TemplateView.as_view(template_name='benevole/home.html'), name='home'),
    path('', views.Home, name='home'),
    # tout ce qui touche à l'authent
    path('', include('django.contrib.auth.urls')),
    # nos app
    path('benevole/', include('benevole.urls')),
    path('association/', include('association.urls')),
    path('evenement/', include('evenement.urls')),
    # debug perfs en dev
    # path('__debug__/', include(debug_toolbar.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

