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

    Also, for revision which review was never started, there is no review
    objects to fetch, so we need to create some dummy ones for display purpose.

    See https://trello.com/c/CdZF9eAG/174-afficher-la-liste-de-distribution-d-un-document

    Note that this cache is cleared in a signal of the same module.

    """
    reviews = get_all_reviews(revision.document)
    if revision.revision in reviews:
        revision_reviews = reviews[revision.revision]
    else:
        dummy_reviews = get_dummy_reviews(revision)
        if revision.revision in dummy_reviews:
            revision_reviews = dummy_reviews[revision.revision]
        else:
            revision_reviews = []
    return revision_reviews


def get_all_reviews(document):
    """Return a dictionnary of revision indexed reviews."""
    cache_key = 'all_reviews_{}'.format(document.id)
    all_reviews = cache.get(cache_key, None)

    if all_reviews is None:
        qs = Review.objects \
            .filter(document=document) \
            .order_by('revision', 'id') \
            .select_related('reviewer')

        all_reviews = {}
        for revision_id, reviews in groupby(qs, lambda obj: obj.revision):
            all_reviews[revision_id] = list(reviews)

        cache.set(cache_key, all_reviews, 5)

    return all_reviews


def get_dummy_reviews(revision):
    """Return a dictionary of Review objects for."""
    cache_key = 'dummy_reviews_{}'.format(revision.document_id)
    dummy_reviews = cache.get(cache_key, None)

    if dummy_reviews is None:

        revisions = revision.__class__.objects \
            .filter(document=revision.document) \
            .filter(review_start_date=None) \
            .select_related('leader', 'approver') \
            .prefetch_related('reviewers')

        dummy_reviews = {}
        for revision in revisions:
            revision_reviews = []

            for reviewer in revision.reviewers.all():
                revision_reviews.append(Review(
                    role='reviewer',
                    status=Review.STATUSES.void,
                    reviewer=reviewer,
                    document_id=revision.document_id))

            if revision.leader:
                revision_reviews.append(Review(
                    role='leader',
                    status=Review.STATUSES.void,
                    reviewer=revision.leader,
                    document_id=revision.document_id))

            if revision.approver:
                revision_reviews.append(Review(
                    role='approver',
                    status=Review.STATUSES.void,
                    reviewer=revision.approver,
                    document_id=revision.document_id))

            dummy_reviews[revision.revision] = revision_reviews

        cache.set(cache_key, dummy_reviews, 5)

    return dummy_reviews
