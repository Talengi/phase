# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.db.models.signals import post_migrate

from metadata.handlers import populate_values_list_cache


class MetadataConfig(AppConfig):
    name = 'metadata'

    def ready(self):
        post_migrate.connect(populate_values_list_cache, sender=self)
