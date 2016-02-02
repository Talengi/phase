# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from transmittals import signals


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
