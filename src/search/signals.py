# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete
from django.conf import settings

from elasticsearch.helpers import bulk

from documents.models import Document
from categories.models import Category
from reviews.signals import pre_batch_review, post_batch_review, batch_item_indexed
from search import elastic
from search.utils import index_document, unindex_document, put_category_mapping


def update_index(sender, instance, **kwargs):
    created = kwargs.pop('created')

    # When a document is first created, the Document is saved
    # before the Metadata and MetadataRevision are created.
    # Then, the Document is saved again
    # Thus, we MUST not index the document on the first save, since the
    # metadata and revision does not exist yet
    if not created and instance.is_indexable:
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


_BULK_ACTIONS = None


@receiver(pre_batch_review, dispatch_uid='on_pre_batch_review')
def on_pre_batch_review(sender, **kwargs):
    global _BULK_ACTIONS
    _BULK_ACTIONS = []

    disconnect_signals()


@receiver(post_batch_review, dispatch_uid='on_post_batch_review')
def on_post_batch_review(sender, **kwargs):
    global _BULK_ACTIONS
    bulk(elastic, _BULK_ACTIONS, refresh=True)
    _BULK_ACTIONS = None

    connect_signals()


@receiver(batch_item_indexed, dispatch_uid='on_batch_item_indexed')
def on_batch_item_indexed(sender, metadata, **kwargs):
    global _BULK_ACTIONS
    _BULK_ACTIONS.append({
        '_index': settings.ELASTIC_INDEX,
        '_type': metadata.document.document_type(),
        '_id': metadata.document_id,
        '_source': metadata.jsonified(),
    })


def connect_signals():
    if settings.ELASTIC_AUTOINDEX:
        post_save.connect(update_index, sender=Document, dispatch_uid='update_index')
        pre_delete.connect(remove_from_index, sender=Document, dispatch_uid='remove_from_index')
        post_save.connect(save_mapping, sender=Category, dispatch_uid='put_category_mapping')


def disconnect_signals():
    if settings.ELASTIC_AUTOINDEX:
        post_save.disconnect(update_index, sender=Document, dispatch_uid='update_index')
        pre_delete.disconnect(remove_from_index, sender=Document, dispatch_uid='remove_from_index')
        post_save.disconnect(save_mapping, sender=Category, dispatch_uid='put_category_mapping')


connect_signals()
