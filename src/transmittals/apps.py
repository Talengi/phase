# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig

from documents.signals import document_revised, revision_edited
from transmittals.signals import transmittal_created, transmittal_pdf_generated
from transmittals.handlers import (
    generate_transmittal_pdf, notify_transmittal_recipients,
    notify_transmittal_on_errors, update_related_revisions)
from transmittals.models import OutgoingTransmittal, OutgoingTransmittalRevision


class TransmittalsConfig(AppConfig):
    name = 'transmittals'
    verbose_name = 'Transmittals'

    def ready(self):
        # Update related revisions when outgoing trs is revised
        document_revised.connect(
            update_related_revisions,
            sender=OutgoingTransmittal,
            dispatch_uid='on_revise_trs_update_related_revisions')

        # Generate transmittal pdf
        transmittal_created.connect(
            generate_transmittal_pdf,
            sender=OutgoingTransmittal,
            dispatch_uid='on_create_trs_generate_pdf')
        document_revised.connect(
            generate_transmittal_pdf,
            sender=OutgoingTransmittal,
            dispatch_uid='on_revise_trs_generate_pdf')

        # Notify transmittal recipients
        transmittal_pdf_generated.connect(
            notify_transmittal_recipients,
            sender=OutgoingTransmittal,
            dispatch_uid='on_transmittal_pdf_notify_recipients')

        # Notify when there is an error message
        document_revised.connect(
            notify_transmittal_on_errors,
            sender=OutgoingTransmittal,
            dispatch_uid='on_transmittal_revision_error_notify_recipients')
        revision_edited.connect(
            notify_transmittal_on_errors,
            sender=OutgoingTransmittalRevision,
            dispatch_uid='on_transmittal_edit_error_notify_recipients')
