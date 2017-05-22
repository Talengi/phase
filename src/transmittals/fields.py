# -*- coding: utf-8 -*-



import os

from django.db.models import ManyToManyField

from documents.fields import RevisionClearableFileField
from privatemedia.fields import PrivateFileField


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


def ogt_file_path(og_transmital, filename):
    return "outgoing_trs_archive/{key}.{extension}".format(
        key=og_transmital.document_key,
        extension=filename.split('.')[-1],)


class OgtFileField(PrivateFileField):
    """Custom file field to store outgoing transmittals pdf files."""

    def __init__(self, *args, **kwargs):
        kwargs.update({
            'upload_to': ogt_file_path,
        })
        super(OgtFileField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(OgtFileField, self).deconstruct()
        kwargs['upload_to'] = ogt_file_path
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        defaults = {
            'form_class': RevisionClearableFileField,
        }
        defaults.update(kwargs)
        return super(OgtFileField, self).formfield(**defaults)
