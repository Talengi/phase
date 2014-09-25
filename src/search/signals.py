from django.db.models.signals import post_save, pre_delete
from django.conf import settings

from documents.models import Document
from search.utils import index_document, unindex_document


def update_index(sender, instance, **kwargs):
    created = kwargs.pop('created')

    # When a document is first created, the Document is saved
    # before the Metadata and MetadataRevision are created.
    # Then, the Document is saved again
    # Thus, we MUST not index the document on the first save, since the
    # metadata and revision does not exist yet
    if not created:
        index_document(instance)


def remove_from_index(sender, instance, **kwargs):
    unindex_document(instance)


if settings.ELASTIC_AUTOINDEX:
    post_save.connect(update_index, sender=Document, dispatch_uid='update_index')
    pre_delete.connect(remove_from_index, sender=Document, dispatch_uid='remove_from_index')
