# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig

from documents import signals
from transmittals.handlers import transmittal_post_save, transmittal_revision_update
from transmittals.models import OutgoingTransmittal


class TransmittalsConfig(AppConfig):
    name = 'transmittals'
    verbose_name = 'Transmittals'

    def ready(self):
        signals.document_created.connect(
            transmittal_post_save,
            sender=OutgoingTransmittal)
        signals.document_revised.connect(
            transmittal_post_save,
            sender=OutgoingTransmittal)
        signals.revision_edited.connect(
            transmittal_revision_update,
        )
