from django.contrib import auth
from django.http import HttpResponseRedirect


User = auth.get_user_model()


class UserSwitchMiddleware(object):
    """Comes from https://github.com/imanhodjaev/django-userswitch

    Removes options and HTML generation, adds log out ability.

    BSD Licensed.
    """
    def __init__(self):
        self.auth_backend = 'django.contrib.auth.backends.ModelBackend'

    def process_request(self, request):
        """
        Logout current user and login the user specified in the username.
        """
        # Check if a user switch was requested by using a GET argument.
        # If not, proceed to normal view.
        username = request.GET.get('userswitch', None)
        if username:
            auth.logout(request)
            if username != 'logout':
                user = User.objects.get(username=username)

                # user.backend is needed for the auth.login to work properly
                user.backend = self.auth_backend
                auth.login(request, user)

            # Redirect to the refering URL, if there is one
            if request.META.get('HTTP_REFERER', False):
                return HttpResponseRedirect(request.META['HTTP_REFERER'])
            else:
                return HttpResponseRedirect('/')

    def process_template_response(self, request, response):
        """Add all users in the template to populate the switching list."""
        response.context_data['switching_users'] = User.objects.all()
        return response
