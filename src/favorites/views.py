from django.core.urlresolvers import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView
from django.http import HttpResponse

from accounts.views import LoginRequiredMixin
from .models import Favorite
from .forms import FavoriteForm


class FavoriteList(LoginRequiredMixin, ListView):
    model = Favorite

    def get_context_data(self, **kwargs):
        context = super(FavoriteList, self).get_context_data(**kwargs)
        context.update({
            'favorites_active': True,
        })
        return context

    def get_queryset(self):
        """Filters favorites per authenticated user."""
        return self.model.objects.filter(user=self.request.user)


class FavoriteCreate(LoginRequiredMixin, CreateView):
    model = Favorite
    form_class = FavoriteForm
    success_url = reverse_lazy('favorite_list')

    def form_valid(self, form):
        """
        If the form is valid, returns the id of the item created.
        """
        super(FavoriteCreate, self).form_valid(form)
        return HttpResponse(self.object.id)


class FavoriteDelete(LoginRequiredMixin, DeleteView):
    model = Favorite
    success_url = reverse_lazy('category_list')
