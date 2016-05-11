"""knight URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
from knightapp import views 
admin.autodiscover()


urlpatterns = patterns('', 
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('knightapp.urls')) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    url(r'^repair_tool/$', knightapp.views.home),
    url(r'^accept_file/', 'knightapp.views.accept_file'),
    url(r'^knight/accept_file/$', 'knightapp.views.accept_file'),
    url(r'^knight/run_script/', 'knightapp.views.run_script'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))


