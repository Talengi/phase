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
    url('^password-reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>[\d\w-]+)/$',
        'django.contrib.auth.views.password_reset_confirm',
        name='password_reset_confirm'),
    url('^password-reset-complete/$',
        'django.contrib.auth.views.password_reset_complete',
        name='password_reset_complete'),
)
