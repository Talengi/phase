# -*- coding: utf-8 -*-


from django.apps import AppConfig


class SchedulesConfig(AppConfig):
    name = 'schedules'
    verbose_name = 'Schedules'

    def ready(self):
        from documents import signals
        from schedules.handlers import update_schedule_section

        signals.document_form_saved.connect(update_schedule_section)
