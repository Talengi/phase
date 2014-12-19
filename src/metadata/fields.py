# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.core.exceptions import ImproperlyConfigured, AppRegistryNotReady
from django.db.models.fields import BLANK_CHOICE_DASH
from django.db.utils import DatabaseError
from django.core.cache import cache


def get_choices_from_list(list_index):
    """Creates a list of values from data in db."""
    from .models import ListEntry

    values = cache.get(list_index)
    if values is None:
        try:
            values = ListEntry.objects \
                .select_related('values_list') \
                .filter(values_list__index=list_index) \
                .values_list('index', 'value')

            # Execute query now, so we can catch any database error
            # For example if db does not exists, and we are trying to
            # run manage.py syncdb
            values = [(key, '%s - %s' % (key, value)) for key, value in values]
            cache.set(list_index, values, None)
        except (DatabaseError, AppRegistryNotReady):
            values = None

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

    def _get_choices(self):
        choices = get_choices_from_list(self.list_index)
        return choices if choices else list(BLANK_CHOICE_DASH)
    choices = property(_get_choices)
