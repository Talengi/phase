# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.models import AnonymousUser

import datetime

from django.core.cache import cache

from bookmarks.models import Bookmark


def bookmarks(request):
    """Fetches data required to render reviews menu."""
    user = getattr(request, 'user')
    context = {}

    if not isinstance(user, AnonymousUser):

        context.update({
            'bookmarks': get_bookmarks(request.user),
        })

    return context


def get_bookmarks(user):
    """Get the number of pending reviews for given review step."""
    cache_key = 'bookmarks_%d' % user.id
    bookmarks = cache.get(cache_key)
    if bookmarks is None:
        bookmarks = Bookmark.objects.filter(user=user)
        cache.set(cache_key, bookmarks, None)

    return bookmarks
