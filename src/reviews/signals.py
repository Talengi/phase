# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db.models.signals import post_save, post_delete
from django.core.cache import cache

from reviews.models import Review


def delete_review_count_cache(sender, instance, **kwargs):
    cache_key = 'review_step_count_%d_%s' % (instance.reviewer_id, instance.role)
    cache.delete(cache_key)


post_save.connect(delete_review_count_cache, sender=Review, dispatch_uid='update_review_cache_count_on_save')
post_delete.connect(delete_review_count_cache, sender=Review, dispatch_uid='update_review_cache_count_on_delete')
