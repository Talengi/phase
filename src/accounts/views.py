from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth.views import redirect_to_login

from django.conf import settings


class LoginRequiredMixin(object):
    """Mark the class as requiring a logged user."""
    login_url = settings.LOGIN_URL

    @method_decorator(login_required(login_url=login_url))
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


class PermissionRequiredMixin(object):
    """Mark the class as needing a specific permission."""
    permission_required = None
    login_url = settings.LOGIN_URL
    redirect_field_name = 'next'

    def dispatch(self, request, *args, **kwargs):
        if not self.permission_required:
            raise ImproperlyConfigured('The PermissionRequiredMixin requires a '
                                       'permission_required attribute to be set.')

        has_permission = request.user.has_perm(self.permission_required)

        if not has_permission:
            return redirect_to_login(request.get_full_path(),
                                     self.login_url,
                                     self.redirect_field_name)

        return super(PermissionRequiredMixin, self).dispatch(request, *args, **kwargs)
