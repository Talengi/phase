from django.conf.urls import url
from .forms import EmailAuthenticationForm


urlpatterns = [
    url('^login/$',
        'django.contrib.auth.views.login',
        {'authentication_form': EmailAuthenticationForm},
        name='login'),
    url('^logout/$',
        'django.contrib.auth.views.logout_then_login',
        name='logout'),
    url('^password-reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
        'django.contrib.auth.views.password_reset_confirm',
        name='password_reset_confirm'),
    url('^password-reset-complete/$',
        'django.contrib.auth.views.password_reset_complete',
        name='password_reset_complete'),
    url(r'^password-change/$',
        'django.contrib.auth.views.password_change',
        {'post_change_redirect': '/'},
        name='password_change')
]
