from django.conf.urls import patterns, url

#from knightapp import views

urlpatterns = patterns('knightapp.views',
    url(r'^$', 'index'),
    url(r'^accept_file/$', 'accept_file'),
    url(r'^run_script/$', 'run_script'),
)
