# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.dispatch import receiver
from django.db.models.signals import post_save

from reviews.signals import review_canceled
from discussion.models import Note


@receiver(review_canceled, dispatch_uid='on_review_canceled')
def on_review_canceled(sender, instance, **kwargs):
    notes = Note.objects \
        .filter(document=instance.document) \
        .filter(revision=instance.revision)
    notes.delete()


@receiver(post_save, sender=Note, dispatch_uid='notification_post_save')
def parse_mentions(sender, instance, **kwargs):
    instance.notify_mentionned_users()
