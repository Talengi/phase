# -*- coding: utf-8 -*-
from __future__ import unicode_literals


def transmittal_post_save(instance, **kwargs):
    """When metadata is saved, generate the revision pdf."""
    revision = instance.latest_revision
    if not revision.pdf_file:
        pdf_file = revision.generate_pdf_file()
        revision.pdf_file.save('thiswillbediscarded.pdf', pdf_file)
