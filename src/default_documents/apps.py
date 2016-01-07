# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig

from documents import signals
from default_documents.handlers import cd_post_save
from default_documents.models import ContractorDeliverable


class DefaultDocumentsConfig(AppConfig):
    name = 'default_documents'
    verbose_name = 'Default Documents'

    def ready(self):
        signals.document_form_saved.connect(
            cd_post_save,
            sender=ContractorDeliverable)
