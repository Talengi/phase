# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig

from documents import signals
from default_documents.handlers import update_schedule_section
from default_documents.models import ContractorDeliverable


class DefaultDocumentsConfig(AppConfig):
    name = 'default_documents'
    verbose_name = 'Default Documents'

    def ready(self):
        signals.document_form_saved.connect(
            update_schedule_section,
            sender=ContractorDeliverable)
