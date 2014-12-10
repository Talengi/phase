# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.dispatch import receiver

from reviews.signals import review_canceled
from discussion.models import Note


@receiver(review_canceled, dispatch_uid='on_review_canceled')
def on_review_canceled(sender, instance, **kwargs):
    notes = Note.objects \
        .filter(document=instance.document) \
        .filter(revision=instance.revision)
    notes.delete()
