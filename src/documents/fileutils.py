from django.core.files.storage import FileSystemStorage
from django.conf import settings


def revision_file_path(revision, filename):
    """Rename document files on upload to match a custom filename

    based on the document number and the revision.

    """
    return "{key}_{revision}.{extension}".format(
        key=revision.document.document_key,
        revision=revision.name,
        extension=filename.split('.')[-1]
    )


def leader_comments_file_path(revision, filename):
    """Rename document files on upload to match a custom filename

    based on the document number and the revision.

    """
    return "{key}_{revision}_leader_comments.{extension}".format(
        key=revision.document.document_key,
        revision=revision.name,
        extension=filename.split('.')[-1]
    )


def approver_comments_file_path(revision, filename):
    """Rename document files on upload to match a custom filename

    based on the document number and the revision.

    """
    return "{key}_{revision}_GTG_comments.{extension}".format(
        key=revision.document.document_key,
        revision=revision.name,
        extension=filename.split('.')[-1]
    )


# Revision documents
private_storage = FileSystemStorage(location=settings.REVISION_FILES_ROOT,
                                    base_url=settings.REVISION_FILES_URL)
