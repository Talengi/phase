from django.views.generic import ListView

from accounts.views import LoginRequiredMixin
from .models import Category


class CategoryList(LoginRequiredMixin, ListView):
    """Display a list of user categories"""

    def get_queryset(self, **kwargs):
        qs = Category.objects \
            .filter(users=self.request.user) \
            .select_related('category_template', 'organisation') \
            .order_by('organisation__name')

        return qs
