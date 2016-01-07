# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig

from documents import signals
from schedules.handlers import update_schedule_section


class SchedulesConfig(AppConfig):
    name = 'schedules'
    verbose_name = 'Schedules'

    def ready(self):
        signals.document_form_saved.connect(update_schedule_section)
