# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from transmittals.models import ExportedRevision, TransmittableMixin


def transmittal_post_save(document, metadata, revision, **kwargs):
    """When metadata is saved, generate the revision pdf."""
    if not revision.pdf_file:
        pdf_file = revision.generate_pdf_file()
        revision.pdf_file.save('thiswillbediscarded.pdf', pdf_file)


def transmittal_revision_update(document, metadata, revision, **kwargs):
    """When a document revision is edited, we need to update the transmittal."""
    sender = kwargs.get('sender')
    if issubclass(sender, TransmittableMixin):
        ExportedRevision.objects \
            .filter(document=document) \
            .filter(revision=revision.revision) \
            .update(
                status=revision.status,
                return_code=revision.get_final_return_code())
