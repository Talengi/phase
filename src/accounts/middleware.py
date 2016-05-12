# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import AnonymousUser

from categories.models import Category


class CategoryMiddleware(object):
    """Add category data to every request."""

    def process_request(self, request):
        user = getattr(request, 'user')
        if not isinstance(user, AnonymousUser):
            request.user_categories = Category.objects \
                .filter(users=user) \
                .select_related('category_template', 'organisation') \
                .order_by('organisation__name', 'category_template__name')
