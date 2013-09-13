from django.conf.urls import patterns, url


urlpatterns = patterns(
    '',
    url('^login/$',
        'django.contrib.auth.views.login',
        name='login'),
    url('^logout/$',
        'django.contrib.auth.views.logout_then_login',
        name='logout'),
)
