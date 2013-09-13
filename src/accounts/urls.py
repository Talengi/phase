from django.conf.urls import patterns, url
from .forms import EmailAuthenticationForm


urlpatterns = patterns(
    '',
    url('^login/$',
        'django.contrib.auth.views.login',
        {'authentication_form': EmailAuthenticationForm},
        name='login'),
    url('^logout/$',
        'django.contrib.auth.views.logout_then_login',
        name='logout'),
)
