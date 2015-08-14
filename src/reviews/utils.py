# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from itertools import groupby

from django.core.cache import cache

from reviews.models import Review


def get_cached_reviews(revision):
    """Get all reviews for the given revision.

    This method is intended to be used when one want to fetch all reviews for
    all the document's revisions successively.

    All the reviews will be fetched in a single query and cached.

    """
    reviews = get_all_reviews(revision.document_id)
    if revision.revision in reviews:
        revision_reviews = reviews[revision.revision]
    else:
        revision_reviews = []
    return revision_reviews


def get_all_reviews(document_id):
    """Return a dictionnary of revision indexed reviews."""
    cache_key = 'all_reviews_{}'.format(document_id)
    all_reviews = cache.get(cache_key, None)

    if all_reviews is None:
        qs = Review.objects \
            .filter(document_id=document_id) \
            .order_by('revision', 'id') \
            .select_related('reviewer')

        all_reviews = {}
        for revision_id, reviews in groupby(qs, lambda obj: obj.revision):
            all_reviews[revision_id] = list(reviews)

        cache.set(cache_key, all_reviews, 60)

    return all_reviews
