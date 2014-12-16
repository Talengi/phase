# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete
from django.conf import settings

from documents.models import Document
from categories.models import Category
from reviews.signals import pre_batch_review, post_batch_review, batch_item_indexed
from search.utils import index_document, unindex_document, put_category_mapping


def update_index(sender, instance, **kwargs):
    created = kwargs.pop('created')

    # When a document is first created, the Document is saved
    # before the Metadata and MetadataRevision are created.
    # Then, the Document is saved again
    # Thus, we MUST not index the document on the first save, since the
    # metadata and revision does not exist yet
    if not created:
        index_document.delay(
            instance.pk,
            instance.document_type(),
            instance.to_json())


def remove_from_index(sender, instance, **kwargs):
    unindex_document.delay(instance.pk, instance.document_type())


def save_mapping(sender, instance, **kwargs):
    created = kwargs.pop('created')
    if created:
        put_category_mapping.delay(instance.pk)


@receiver(pre_batch_review, dispatch_uid='on_pre_batch_review')
def on_pre_batch_review(sender, **kwargs):
    disconnect_signals()


@receiver(post_batch_review, dispatch_uid='on_post_batch_review')
def on_post_batch_review(sender, **kwargs):
    connect_signals()


@receiver(batch_item_indexed, dispatch_uid='on_batch_item_indexed')
def on_batch_item_indexed(sender, metadata, **kwargs):
    index_document(
        metadata.document_id,
        metadata.document.document_type(),
        metadata.document.to_json())


def connect_signals():
    post_save.connect(update_index, sender=Document, dispatch_uid='update_index')
    pre_delete.connect(remove_from_index, sender=Document, dispatch_uid='remove_from_index')
    post_save.connect(save_mapping, sender=Category, dispatch_uid='put_category_mapping')


def disconnect_signals():
    post_save.disconnect(update_index, sender=Document, dispatch_uid='update_index')
    pre_delete.disconnect(remove_from_index, sender=Document, dispatch_uid='remove_from_index')
    post_save.disconnect(save_mapping, sender=Category, dispatch_uid='put_category_mapping')


if settings.ELASTIC_AUTOINDEX:
    connect_signals()
