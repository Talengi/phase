from django.core.files.storage import FileSystemStorage
from django.conf import settings


def upload_to_path(instance, filename):
    """Rename document files on upload to match a custom filename

    based on the document number and the revision."""
    return "{number}_{revision}.{extension}".format(
        number=instance.document.document_number,
        revision=instance.revision,
        extension=filename.split('.')[-1]
    )

# Revision documents
private_storage = FileSystemStorage(location=settings.REVISION_FILES_ROOT,
                                    base_url=settings.REVISION_FILES_URL)
