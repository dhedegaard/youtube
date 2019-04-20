from __future__ import unicode_literals

from django.conf.urls import url
from django.contrib.auth import views as auth_views

from youtube import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^channel/(?P<author>.+)/$', views.channel, name='channel'),
    url(r'^admin/$', views.admin, name='admin'),
    url(r'^admin/(?P<channelid>\d+)/delete/$', views.channel_delete,
        name='channel-delete'),
    url(r'^admin/(?P<channelid>\d+)/toggle-hidden/$',
        views.toggle_hidden, name='toggle-hidden'),
    url(r'^admin/(?P<channelid>\d+)/full-fetch/$',
        views.channel_fetch, name='channel-full-fetch', kwargs={
            'full_fetch': True,
        }),
    url(r'^admin/(?P<channelid>\d+)/fetch/$',
        views.channel_fetch, name='channel-fetch'),
    url(r'^admin/add/$', views.channel_add, name='channel-add'),
    url(r'^login/$',
        auth_views.LoginView.as_view(template_name='youtube/login.html'),
        name='login'),
    url(r'^logout/$',
        auth_views.LogoutView.as_view(next_page='/'),
        name='logout'),
]
