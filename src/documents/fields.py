from django.db import models
from django.forms import fields

from documents.fileutils import (
    private_storage, revision_file_path, leader_comments_file_path,
    approver_comments_file_path
)
from documents.widgets import PhaseClearableFileInput


class PrivateFileField(models.FileField):
    """Store files in a private dir."""
    def __init__(self, *args, **kwargs):
        kwargs.update({
            'storage': private_storage,
        })
        return super(PrivateFileField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {
            'form_class': PhaseClearableFileField,
            'max_length': self.max_length,
        }
        if 'initial' in kwargs:
            defaults['required'] = False
        defaults.update(kwargs)
        return super(PrivateFileField, self).formfield(**defaults)


class RevisionFileField(PrivateFileField):
    """Custom file field to store revision files."""

    def __init__(self, *args, **kwargs):
        kwargs.update({
            'upload_to': revision_file_path,
        })
        return super(RevisionFileField, self).__init__(*args, **kwargs)


class LeaderCommentsFileField(PrivateFileField):
    """Custom file field to store leader comments files."""

    def __init__(self, *args, **kwargs):
        kwargs.update({
            'upload_to': leader_comments_file_path,
        })
        return super(LeaderCommentsFileField, self).__init__(*args, **kwargs)


class ApproverCommentsFileField(PrivateFileField):
    """Custom file field to store approver comments files."""

    def __init__(self, *args, **kwargs):
        kwargs.update({
            'upload_to': approver_comments_file_path,
        })
        return super(ApproverCommentsFileField, self).__init__(*args, **kwargs)


class PhaseClearableFileField(fields.FileField):
    widget = PhaseClearableFileInput
