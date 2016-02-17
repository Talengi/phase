# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from notifications.models import notify
from transmittals import signals
from transmittals.tasks import do_notify_transmittal_recipients


def generate_transmittal_pdf(document, metadata, revision, **kwargs):
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
    do_notify_transmittal_recipients.delay(metadata.id, revision.id)


def notify_transmittal_on_errors(document, metadata, revision, **kwargs):
    if revision.has_error():
        recipients = metadata.recipient.users.all()
        msg = _('There is an error on transmittal '
                '<a href="%(url)s">%(name)s</a>') % {
                    'url': document.get_absolute_url(),
                    'name': document.title}

        for user in recipients:
            notify(user, msg)
