# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.db.models.signals import post_save

from transmittals.handlers import transmittal_post_save
from transmittals.models import OutgoingTransmittal


class TransmittalsConfig(AppConfig):
    name = 'transmittals'
    verbose_name = 'Transmittals'

    def ready(self):
        post_save.connect(transmittal_post_save, sender=OutgoingTransmittal)
