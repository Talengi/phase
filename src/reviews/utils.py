# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from itertools import groupby

from reviews.models import Review


__REVIEWS__ = None


def get_cached_reviews(revision):
    """Get all reviews for the given revision.

    This method is intended to be used when one want to fetch all reviews for
    all the document's revisions successively.

    All the reviews will be fetched in a single query and cached.

    """
    global __REVIEWS__
    if __REVIEWS__ is None:
        all_reviews = Review.objects \
            .filter(document=revision.document) \
            .order_by('revision', 'id') \
            .select_related('reviewer')

        __REVIEWS__ = {}
        for revision_id, reviews in groupby(all_reviews, lambda obj: obj.revision):
            __REVIEWS__[revision_id] = list(reviews)

    if revision.revision in __REVIEWS__:
        reviews = __REVIEWS__[revision.revision]
    else:
        reviews = []
    return reviews
