from django.contrib.auth.decorators import login_required


class LoginRequiredMixin(object):
    """Mark the class as requiring a logged user."""
    @classmethod
    def as_view(cls):
        return login_required(super(LoginRequiredMixin, cls).as_view())
