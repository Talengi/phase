# -*- coding: utf-8 -*-


from django.apps import AppConfig
from django.db.models.signals import post_migrate


class MetadataConfig(AppConfig):
    name = 'metadata'
    db_is_ready = False

    def ready(self):
        from metadata.handlers import save_db_state, populate_values_list_cache
        # Hooking to post_migrate is the only way I've found to
        # make sure the db is really available and can be queried
        # to populate the values list cache
        post_migrate.connect(save_db_state, sender=self)
        post_migrate.connect(populate_values_list_cache, sender=self)
