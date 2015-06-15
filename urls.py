from __future__ import unicode_literals

from django.conf.urls import patterns, url

from youtube import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^channel/(?P<author>.+)/$', views.channel, name='channel'),
    url(r'^admin/$', views.admin, name='admin'),
    url(r'^admin/(?P<channelid>\d+)/delete/$', views.channel_delete,
        name='channel-delete'),
    url(r'^admin/(?P<channelid>\d+)/toggle-hidden/$',
        views.toggle_hidden, name='toggle-hidden'),
    url(r'^admin/add/$', views.channel_add, name='channel-add'),
    url(r'^login/$', 'django.contrib.auth.views.login', {
        'template_name': 'youtube/login.html',
        'current_app': 'youtube',
    }, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {
        'next_page': '/',
        'current_app': 'youtube',
    }, name='logout'),
)
