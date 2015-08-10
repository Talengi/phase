# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache

from dashboards.models import Dashboard


def dashboards(request):
    """Fetch and cache data required to render the dashboards menu."""
    user = getattr(request, 'user')
    context = {}

    if not isinstance(user, AnonymousUser):
        context.update({
            'user_dashboards': get_user_dashboards(user)
        })
    return context


def get_user_dashboards(user):
    cache_key = 'user_{}_dashboards'.format(user.id)
    dashboards = cache.get(cache_key)

    if dashboards is None:
        qs = Dashboard.objects \
            .filter(authorized_users=user) \
            .select_related('category__organisation')
        dashboards = [(
            dashboard.category.organisation.name,
            dashboard.title,
            dashboard.get_absolute_url()) for dashboard in qs]
        cache.set(cache_key, dashboards, 500)

    return dashboards
