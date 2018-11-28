# -*- coding: utf-8 -*-


import os

from django.db.models import ManyToManyField
from privatemedia.fields import PrivateFileField, PhaseClearableFileField


def transmittal_upload_to(trs_revision, filename):
    """Move transmittal files to the correct destination.

    We keep the original filename since it's been validated
    before.

    """
    return 'transmittals/{transmittal}/{filename}'.format(
        transmittal=trs_revision.transmittal.document_key,
        filename=os.path.basename(filename))


class TransmittalFileField(PrivateFileField):
    """Store fields for transmittals waiting to be processed."""

    def __init__(self, *args, **kwargs):
        kwargs.update({
            'upload_to': transmittal_upload_to,
        })
        return super(TransmittalFileField, self).__init__(*args, **kwargs)


class ManyDocumentsField(ManyToManyField):
    """Useless field.

    Kept only for migrations compatibility.

    """
    pass


class OgtBaseFileField(PrivateFileField):
    """Custom file field to store outgoing transmittals pdf files."""

    def __init__(self, *args, **kwargs):
        kwargs.update({
            'upload_to': self.get_upload_to(),
        })
        super(OgtBaseFileField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(OgtBaseFileField, self).deconstruct()
        kwargs['upload_to'] = self.get_upload_to()
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        defaults = {
            'form_class': PhaseClearableFileField,
        }
        defaults.update(kwargs)
        return super(OgtBaseFileField, self).formfield(**defaults)


def ogt_file_path(og_transmital, filename):
    return "outgoing_trs_archive/{key}.{extension}".format(
        key=og_transmital.document_key,
        extension=filename.split('.')[-1], )


class OgtFileField(OgtBaseFileField):
    """Custom file field to store outgoing transmittals pdf files."""

    def get_upload_to(self):
        return ogt_file_path


def client_comments_file_path(revision, filename):
    """Build a path with this pattern: client_comments/<document number>_<revision name>_comments.{ext>"""
    return "client_comments/{document_number}_{revision_name}_comments.{extension}".format(
        document_number=revision.document,
        revision_name=revision.name,
        extension=filename.split('.')[-1], )


class ClientCommentsFileField(OgtBaseFileField):
    """Custom field to store client comments."""
    def get_upload_to(self):
        return client_comments_file_path
