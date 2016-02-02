# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from transmittals import signals
from transmittals.tasks import do_notify_transmittal_recipients


def transmittal_post_save(document, metadata, revision, **kwargs):
    """When metadata is saved, generate the revision pdf."""
    if not revision.pdf_file:
        pdf_file = revision.generate_pdf_file()
        revision.pdf_file.save('thiswillbediscarded.pdf', pdf_file)

        signals.transmittal_pdf_generated.send(
            document=document,
            metadata=metadata,
            revision=revision,
            sender=metadata.__class__)


def notify_transmittal_recipients(document, metadata, revision, **kwargs):
    do_notify_transmittal_recipients.delay(revision.id)
