# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from notifications.models import mass_notify
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
    if hasattr(revision, '_send_error_notifications'):
        recipients = metadata.recipient.users.all()
        msg = _('There is an error on transmittal '
                '<a href="%(url)s">%(name)s</a>') % {
                    'url': document.get_absolute_url(),
                    'name': document.title}

        mass_notify(recipients, msg)


def update_related_revisions(document, **kwargs):
    """"When a revision is created on an outgoing transmittal, we append the
    last related documents revisions to it and we perform the due date
    computation by calling `link_to_revisions` method."""
    revisions_class = document.metadata.get_revisions_class()
    rev_list = []
    linked_revs = revisions_class.objects.filter(transmittals=document.metadata)
    for rev in linked_revs:
        rev_list.append(rev.metadata.latest_revision)
    rev_list = list(set(rev_list))
    document.metadata.link_to_revisions(rev_list)
