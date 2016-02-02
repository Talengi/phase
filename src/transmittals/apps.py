# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig

from documents.signals import document_revised
from transmittals.signals import transmittal_created, transmittal_pdf_generated
from transmittals.handlers import (
    transmittal_post_save, notify_transmittal_recipients)
from transmittals.models import OutgoingTransmittal


class TransmittalsConfig(AppConfig):
    name = 'transmittals'
    verbose_name = 'Transmittals'

    def ready(self):
        transmittal_created.connect(
            transmittal_post_save,
            sender=OutgoingTransmittal)
        document_revised.connect(
            transmittal_post_save,
            sender=OutgoingTransmittal)

        transmittal_pdf_generated.connect(
            notify_transmittal_recipients,
            sender=OutgoingTransmittal)
