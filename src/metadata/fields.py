# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.db.models.fields import BLANK_CHOICE_DASH
from django.core.cache import cache

from metadata.handlers import populate_values_list_cache


def get_choices_from_list(list_index):
    """Load the values list from cache.

    Cache is populated post-syncdb

    """
    cache_key = 'values_list_{}'.format(list_index)

    # If the database is ready but the cache was
    # not populate yet
    app = apps.get_app_config('metadata')
    if cache_key not in cache and app.db_is_ready:
        populate_values_list_cache()

    values = cache.get(cache_key, [])
    if not values:
        cache.delete(cache_key)

    return values


class ConfigurableChoiceField(models.CharField):
    def __init__(self, *args, **kwargs):
        self.list_index = kwargs.pop('list_index', None)
        if self.list_index is None:
            raise ImproperlyConfigured('Missing field: list_index')
        defaults = {
            'max_length': 50,
            'choices': None,
        }
        defaults.update(kwargs)
        super(ConfigurableChoiceField, self).__init__(*args, **defaults)

    def deconstruct(self):
        name, path, args, kwargs = super(ConfigurableChoiceField, self).deconstruct()
        kwargs['list_index'] = self.list_index
        return name, path, args, kwargs

    def _get_choices(self):
        choices = get_choices_from_list(self.list_index)
        return choices if choices else list(BLANK_CHOICE_DASH)
    choices = property(_get_choices)
