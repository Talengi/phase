# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.dispatch import Signal, receiver
from django.db.models.signals import post_save, post_delete
from django.core.cache import cache

from reviews.models import Review


review_canceled = Signal()
pre_batch_review = Signal()
post_batch_review = Signal(providing_args=['user_id'])
batch_item_indexed = Signal(providing_args=['document_type, document_id, json'])


def delete_review_count_cache(sender, instance, **kwargs):
    cache_key = 'review_step_count_%d_%s' % (instance.reviewer_id, instance.role)
    cache.delete(cache_key)

    cache_key = 'review_step_count_%d_priorities' % instance.reviewer_id
    cache.delete(cache_key)

post_save.connect(delete_review_count_cache, sender=Review, dispatch_uid='update_review_cache_count_on_save')
post_delete.connect(delete_review_count_cache, sender=Review, dispatch_uid='update_review_cache_count_on_delete')


@receiver(post_batch_review, dispatch_uid='update_review_cache_count_on_batch')
def delete_all_review_cache(sender, user_id, **kwargs):
    """Delete review count cache after a batch review."""
    roles = [key for key, value in Review.ROLES]
    for role in roles:
        cache_key = 'review_step_count_%d_%s' % (user_id, role)
        cache.delete(cache_key)

    cache_key = 'review_step_count_%d_priorities' % (user_id)
    cache.delete(cache_key)
