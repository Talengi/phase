from django.core.files.storage import FileSystemStorage
from django.conf import settings


def upload_to_path(revision, filename):
    """Rename document files on upload to match a custom filename

    based on the document number and the revision."""
    return "{key}_{revision}.{extension}".format(
        key=revision.document.document_key,
        revision=revision.revision,
        extension=filename.split('.')[-1]
    )

# Revision documents
private_storage = FileSystemStorage(location=settings.REVISION_FILES_ROOT,
                                    base_url=settings.REVISION_FILES_URL)
