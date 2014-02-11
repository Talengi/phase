from django.db import models
from django.forms import fields

from documents.fileutils import upload_to_path, private_storage
from documents.widgets import PhaseClearableFileInput


class RevisionFileField(models.FileField):
    """Custom file field to store revision files.

    We only define this to override the default widget.

    """

    def __init__(self, *args, **kwargs):
        kwargs.update({
            'upload_to': upload_to_path,
            'storage': private_storage,
        })
        return super(RevisionFileField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {
            'form_class': PhaseClearableFileField,
            'max_length': self.max_length,
        }
        if 'initial' in kwargs:
            defaults['required'] = False
        defaults.update(kwargs)
        return super(RevisionFileField, self).formfield(**defaults)


class PhaseClearableFileField(fields.FileField):
    widget = PhaseClearableFileInput
