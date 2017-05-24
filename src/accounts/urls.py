from django.conf.urls import url
from django.contrib.auth import views as auth_views

from .forms import EmailAuthenticationForm


urlpatterns = [
    url('^login/$',
        auth_views.login,
        {'authentication_form': EmailAuthenticationForm},
        name='login'),
    url('^logout/$',
        auth_views.logout_then_login,
        name='logout'),
    url('^password-reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
        auth_views.password_reset_confirm,
        name='password_reset_confirm'),
    url('^password-reset-complete/$',
        auth_views.password_reset_complete,
        name='password_reset_complete'),
    url(r'^password-change/$',
        auth_views.password_change,
        {'post_change_redirect': '/'},
        name='password_change')
]
