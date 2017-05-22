# -*- coding: utf-8 -*-


from django.core.cache import cache


def get_cache_key(document, revision):
    cache_key = 'discussion_length_{}_{}'.format(document.pk, revision)
    return cache_key


def get_discussion_length(revision):
    """Get the number of remarkes on a revision.

    This is a helper method to return a cached value. Settings the cache must
    be done elsewhere. (Currently in discussion/signals.py/update_cache.)

    """
    cache_key = get_cache_key(revision.document, revision.revision)
    length = cache.get(cache_key, 0)
    return length
