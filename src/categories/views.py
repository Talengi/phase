# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import ListView
from django.http import Http404

from braces.views import LoginRequiredMixin
from annoying.functions import get_object_or_None

from .models import Category


class CategoryList(LoginRequiredMixin, ListView):
    """Display a list of user categories"""

    template_name = 'categories/category_list.html'

    def get_queryset(self, **kwargs):
        # The category list we will use is set un a context processor
        # See `accounts/context_processors.py`
        return []


class CategoryMixin(object):
    """Use this mixin to extract the category in url."""

    def dispatch(self, request, *args, **kwargs):
        self.extract_category()
        return super(CategoryMixin, self).dispatch(request, *args, **kwargs)

    def extract_category(self):
        """Set the `self.category` variable."""
        organisation_slug = self.kwargs['organisation']
        category_slug = self.kwargs['category']

        qs = Category.objects \
            .select_related() \
            .filter(users=self.request.user) \
            .filter(organisation__slug=organisation_slug) \
            .filter(category_template__slug=category_slug)
        self.category = get_object_or_None(qs)
        if self.category is None:
            raise Http404('Category not found')

    def get_context_data(self, **kwargs):
        context = super(CategoryMixin, self).get_context_data(**kwargs)
        context.update({
            'category': self.category,
            'organisation_slug': self.kwargs['organisation'],
            'category_slug': self.kwargs['category'],
        })
        return context
