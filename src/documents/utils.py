import zipfile
import tempfile

from django.contrib.contenttypes.models import ContentType
from django.db import transaction


@transaction.atomic
def save_document_forms(metadata_form, revision_form, category, **doc_kwargs):
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
        return create_document_from_forms(metadata_form, revision_form, category, **doc_kwargs)
    elif revision.pk is None:
        return create_revision_from_forms(metadata_form, revision_form, category)
    else:
        return update_revision_from_forms(metadata_form, revision_form, category)


def create_document_from_forms(metadata_form, revision_form, category, **doc_kwargs):
    """Creates a brand new document"""
    from documents.models import Document

    revision = revision_form.save(commit=False)
    metadata = metadata_form.save(commit=False)

    key = metadata.document_key or metadata.generate_document_key()
    document = Document.objects.create(
        document_key=key,
        category=category,
        current_revision=revision.revision,
        current_revision_date=revision.revision_date,
        **doc_kwargs)

    revision.document = document
    revision.save()
    revision_form.save_m2m()

    metadata.document = document
    metadata.latest_revision = revision
    metadata.save()
    metadata_form.save_m2m()

    return document, metadata, revision


def create_revision_from_forms(metadata_form, revision_form, category):
    """Updates an existing document and creates a new revision."""
    revision = revision_form.save(commit=False)
    metadata = metadata_form.save(commit=False)
    document = metadata.document

    revision.revision = metadata.latest_revision.revision + 1
    revision.document = document
    revision.save()
    revision_form.save_m2m()

    metadata.latest_revision = revision
    metadata.save()
    metadata_form.save_m2m()

    document.current_revision = revision.revision
    document.current_revision_date = revision.revision_date
    document.save()

    return document, metadata, revision


def update_revision_from_forms(metadata_form, revision_form, category):
    """Updates and existing document and revision."""
    revision = revision_form.save()
    metadata = metadata_form.save()
    document = metadata.document

    return document, metadata, revision


# HACK to fix http://hg.python.org/cpython/rev/4f0988e8fcb1/
class FixedZipFile(zipfile.ZipFile):
    """Old versions of Python don't have the patch merged."""
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()


def compress_documents(documents, format='both', revisions='latest'):
    """Compress the given files' documents (or queryset) in a zip file.

    * format can be either 'both', 'native' or 'pdf'
    * revisions can be either 'latest' or 'all'

    Returns the name of the ziped file.
    """
    temp_file = tempfile.TemporaryFile()

    with FixedZipFile(temp_file, mode='w') as zip_file:
        files = []
        for document in documents:
            if revisions == 'latest':
                revs = [document.latest_revision]
            elif revisions == 'all':
                revs = document.get_all_revisions()

            for rev in revs:
                if rev is not None:
                    if format in ('native', 'both'):
                        files.append(rev.native_file)
                    if format in ('pdf', 'both'):
                        files.append(rev.pdf_file)

        for file_ in files:
            if file_.name:
                zip_file.write(
                    file_.path,
                    file_.name,
                    compress_type=zipfile.ZIP_DEFLATED
                )
    return temp_file


def stringify_value(val):
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

    >>> stringify_value(None)
    u'NC'
    """
    if val is None:
        unicode_val = u'NC'
    elif type(val) == bool:
        unicode_val = u'Yes' if val else u'No'
    else:
        unicode_val = unicode(val)

    return unicode_val


def get_all_document_classes():
    """Returns all document classes available."""
    qs = ContentType.objects \
        .filter(app_label__endswith='_documents') \
        .exclude(model__icontains='revision')

    klasses = [content_type.model_class() for content_type in qs]
    return klasses


def get_all_revision_classes():
    """Returns all classes inheriting MetadataRevision."""
    qs = ContentType.objects \
        .filter(app_label__endswith='_documents') \
        .filter(model__icontains='revision')

    klasses = [content_type.model_class() for content_type in qs]
    return klasses
