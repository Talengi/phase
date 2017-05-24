# -*- coding: utf-8 -*-



from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.core.cache import cache

from reviews.signals import review_canceled
from discussion.utils import get_cache_key
from discussion.models import Note


@receiver(review_canceled, dispatch_uid='on_review_canceled_clear_remarks')
def clear_remarks(sender, instance, **kwargs):
    notes = Note.objects \
        .filter(document=instance.document) \
        .filter(revision=instance.revision)
    notes.delete()


@receiver(review_canceled, dispatch_uid='on_review_canceled_update_cache')
def clear_cache(sender, instance, **kwargs):
    cache_key = get_cache_key(instance.document, instance.revision)
    cache.delete(cache_key)


@receiver(post_save, sender=Note, dispatch_uid='on_remark_notify_users')
def parse_mentions(sender, instance, **kwargs):
    instance.notify_mentionned_users()


@receiver(post_save, sender=Note, dispatch_uid='on_new_remark_update_cache')
@receiver(post_delete, sender=Note, dispatch_uid='on_delete_remark_notify_users')
def update_cache(sender, instance, **kwargs):
    cache_key = get_cache_key(instance.document, instance.revision)
    discussion_length = Note.objects \
        .filter(document=instance.document) \
        .filter(revision=instance.revision) \
        .count()
    cache.set(cache_key, discussion_length, None)
