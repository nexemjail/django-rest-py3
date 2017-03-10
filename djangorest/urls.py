"""djangorest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.views.generic import TemplateView
from .views import ObtainJSONWebToken

from users.api import urls as api_urls

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^index/$', TemplateView.as_view(template_name='index.html')),
    url(r'^auth/$', ObtainJSONWebToken.as_view(), name='auth'),
    url(r'^events/', include('events.urls', namespace='events')),
    url(r'^users/', include('users.urls', namespace='users')),
    url(r'^', include(api_urls)),

]


if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    from django.conf.urls.static import static

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


