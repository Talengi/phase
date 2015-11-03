# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig

from transmittals.handlers import transmittal_post_save
from transmittals.signals import related_documents_saved
from transmittals.models import OutgoingTransmittal


class TransmittalsConfig(AppConfig):
    name = 'transmittals'
    verbose_name = 'Transmittals'

    def ready(self):
        related_documents_saved.connect(
            transmittal_post_save,
            sender=OutgoingTransmittal)
