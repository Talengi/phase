from django.views.generic import ListView
from django.utils.translation import ugettext_lazy as _

from accounts.views import LoginRequiredMixin
from .models import Favorite


class FavoriteList(LoginRequiredMixin, ListView):
    model = Favorite

    def breadcrumb_section(self):
        return _('Favorites')

    def get_context_data(self, **kwargs):
        context = super(FavoriteList, self).get_context_data(**kwargs)
        context.update({
            'favorites_active': True,
        })
        return context

    def get_queryset(self):
        """Filters favorites per authenticated user."""
        return self.model.objects.filter(user=self.request.user)
