from django.conf.urls import url, include


urlpatterns = [
    url('^', include('users.api.urls')),
]