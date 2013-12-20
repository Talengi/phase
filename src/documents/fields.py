from django.db import models

from documents.fileutils import upload_to_path, private_storage


class RevisionFileField(models.FileField):
    """Custom file field to store revision files."""
    def __init__(self, *args, **kwargs):
        kwargs.update({
            'upload_to': upload_to_path,
            'storage': private_storage,
        })
        return super(RevisionFileField, self).__init__(*args, **kwargs)
