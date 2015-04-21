from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^$', 'youtube.views.index', name='index'),
    url(r'^admin/$', 'youtube.views.admin', name='admin'),
    url(r'^admin/(?P<channelid>\d+)/delete/$', 'youtube.views.channel_delete',
        name='channel-delete'),
    url(r'^admin/(?P<channelid>\d+)/toggle-hidden/$',
        'youtube.views.toggle_hidden', name='toggle-hidden'),
    url(r'^admin/add/$', 'youtube.views.channel_add', name='channel-add'),
    url(r'^login/$', 'django.contrib.auth.views.login', {
        'template_name': 'youtube/login.html',
        'current_app': 'youtube',
    }, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {
        'next_page': '/',
        'current_app': 'youtube',
    }, name='logout'),
)
