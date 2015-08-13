# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.db.models.signals import post_migrate

from metadata.handlers import save_db_state, populate_values_list_cache


class MetadataConfig(AppConfig):
    name = 'metadata'
    db_is_ready = False

    def ready(self):
        # Hooking to post_migrate is the only way I've found to
        # make sure the db is really available and can be queried
        # to populate the values list cache
        post_migrate.connect(save_db_state, sender=self)
        post_migrate.connect(populate_values_list_cache, sender=self)
