# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from documents.fields import PrivateFileField


def transmittal_upload_to(trs_revision, filename):
    """Move transmittal files to the correct destination.

    We keep the original filename since it's been validated
    before.

    `filename` is of Unipath type.

    """

    return 'transmittals/{transmittal}/{filename}'.format(
        transmittal=trs_revision.transmittal.transmittal_key,
        filename=filename.name)


class TransmittalFileField(PrivateFileField):
    """Store fields for transmittals waiting to be processed."""

    def __init__(self, *args, **kwargs):
        kwargs.update({
            'upload_to': transmittal_upload_to,
        })
        return super(TransmittalFileField, self).__init__(*args, **kwargs)
