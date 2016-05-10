# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_text
from django.utils import timezone
from django.db import transaction

from documents import signals


def save_document_forms(metadata_form, revision_form, category, rewrite_schedule=True, **doc_kwargs):
    """Creates or updates a document from it's different forms.

    Two forms are necessary to edit a document : the metadata and revision forms.

    There are multiple cases to handle:

      * We are creating a completely new document
      * We are creating a new revision of an existing document
      * We are editing an existing revision

    """
    if not metadata_form.is_valid():
        raise RuntimeError('Metadata form MUST be valid. \
                           ({})'.format(metadata_form.errors))

    if not revision_form.is_valid():
        raise RuntimeError('Revision form MUST be valid. \
                           ({})'.format(revision_form.errors))

    revision = revision_form.save(commit=False)
    metadata = metadata_form.save(commit=False)

    # Those three functions could be regrouped, but they form
    # an if / else russian mountain
    if metadata.pk is None:
        doc, meta, rev = create_document_from_forms(
            metadata_form, revision_form, category, **doc_kwargs)
    elif revision.pk is None:
        doc, meta, rev = create_revision_from_forms(
            metadata_form, revision_form, category)
    else:
        doc, meta, rev = update_revision_from_forms(
            metadata_form, revision_form, category)

    signals.document_form_saved.send(
        document=doc,
        metadata=meta,
        revision=rev,
        rewrite_schedule=rewrite_schedule,
        sender=doc.__class__)

    return doc, meta, rev


def create_document_from_forms(metadata_form, revision_form, category, **doc_kwargs):
    """Creates a brand new document"""
    from documents.models import Document

    with transaction.atomic():
        revision = revision_form.save(commit=False)
        revision.revision = revision.get_first_revision_number()
        metadata = metadata_form.save(commit=False)

        # Extract the manually submitted document key, or generate one
        # if the field was left empty.
        doc_number = metadata.document_number
        if doc_number:
            doc_key = metadata.document_key
        else:
            doc_number = metadata.generate_document_key()
            doc_key = doc_number

        document = Document.objects.create(
            document_key=doc_key,
            document_number=doc_number,
            category=category,
            current_revision=revision.revision,
            current_revision_date=revision.revision_date,
            updated_on=timezone.now(),
            title=metadata.title,
            **doc_kwargs)

        metadata.document = document
        metadata.document_key = doc_key
        metadata.document_number = doc_number
        metadata.save()
        metadata_form.save_m2m()

        revision.metadata = metadata
        revision.save()
        revision_form.save_m2m()

        metadata.latest_revision = revision
        metadata.save()

    signals.document_created.send(
        document=document,
        metadata=metadata,
        revision=revision,
        sender=metadata.__class__)
    return document, metadata, revision


def create_revision_from_forms(metadata_form, revision_form, category):
    """Updates an existing document and creates a new revision."""
    with transaction.atomic():
        revision = revision_form.save(commit=False)
        metadata = metadata_form.save(commit=False)
        document = metadata.document

        revision.revision = metadata.latest_revision.revision + 1
        revision.metadata = metadata
        revision.save()
        revision_form.save_m2m()

        metadata.latest_revision = revision
        metadata.save()
        metadata_form.save_m2m()

        document.document_key = metadata.document_key
        document.document_number = metadata.document_number
        document.current_revision = revision.revision
        document.current_revision_date = revision.revision_date
        document.title = metadata.title
        document.updated_on = timezone.now()
        document.save()

    signals.document_revised.send(
        document=document,
        metadata=metadata,
        revision=revision,
        sender=metadata.__class__)

    return document, metadata, revision


def update_revision_from_forms(metadata_form, revision_form, category):
    """Updates and existing document and revision."""
    with transaction.atomic():
        revision = revision_form.save()
        metadata = metadata_form.save()

        document = metadata.document
        document.document_key = metadata.document_key
        document.document_number = metadata.document_number
        document.title = metadata.title
        document.updated_on = timezone.now()
        document.save()

    signals.revision_edited.send(
        document=document,
        metadata=metadata,
        revision=revision,
        sender=revision.__class__)

    return document, metadata, revision


def stringify_value(val, none_val='NC'):
    """Returns a value suitable for display in a document list.

    >>> stringify_value('toto')
    u'toto'

    >>> stringify_value(None)
    u'NC'

    >>> stringify_value(True)
    u'Yes'

    >>> import datetime
    >>> stringify_value(datetime.datetime(2000, 1, 1))
    u'2000-01-01'
    """
    if val is None:
        unicode_val = none_val
    elif type(val) == bool:
        unicode_val = u'Yes' if val else u'No'
    else:
        unicode_val = force_text(val)

    return unicode_val


def get_all_document_types():
    """Return all Metadata content types."""
    from documents.models import Metadata
    return []
    qs = ContentType.objects.all()
    types = [ct for ct in qs if issubclass(ct.model_class(), Metadata)]
    return types


def get_all_document_qs():
    """Return all Metadata subclasses as a queryset."""
    types = get_all_document_types()
    ids = [ct.id for ct in types]
    return ContentType.objects.filter(id__in=ids)


def get_all_document_classes():
    """Return all Metadata subclasses available."""
    classes = [ct.model_class() for ct in get_all_document_types()]
    return classes


def get_all_revision_types():
    """Return all MetadataRevisionBase content types."""
    from documents.models import MetadataRevisionBase
    qs = ContentType.objects.all()
    types = (ct for ct in qs if issubclass(ct.model_class(), MetadataRevisionBase))
    return types


def get_all_revision_classes():
    """Return all MetadataRevisionBase subclasses available."""
    classes = [ct.model_class() for ct in get_all_revision_types()]
    return classes
