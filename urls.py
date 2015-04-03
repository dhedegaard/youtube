from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'youtube.views.index', name='index'),
    url(r'^admin/$', 'youtube.views.admin', name='admin'),
    url(r'^login/$', 'django.contrib.auth.views.login', {
        'template_name': 'youtube/login.html',
        'current_app': 'youtube',
    }, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {
        'next_page': '/',
        'current_app': 'youtube',
    }, name='logout'),
)
