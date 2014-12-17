# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from itertools import groupby

from reviews.models import Review


def get_cached_reviews(revision):
    """Get all reviews for the given revision.

    This method is intended to be used when one want to fetch all reviews for
    all the document's revisions successively.

    All the reviews will be fetched in a single query and cached.

    """
    reviews = get_all_reviews(revision)
    if revision.revision in reviews:
        revision_reviews = reviews[revision.revision]
    else:
        revision_reviews = []
    return revision_reviews


def get_all_reviews(revision):
    """Return a dictionnary of revision indexed reviews."""
    qs = Review.objects \
        .filter(document=revision.document) \
        .order_by('revision', 'id') \
        .select_related('reviewer')

    all_reviews = {}
    for revision_id, reviews in groupby(qs, lambda obj: obj.revision):
        all_reviews[revision_id] = list(reviews)
    return all_reviews
