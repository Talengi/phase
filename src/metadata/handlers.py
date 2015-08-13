# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models import F, Value as V
from django.db.models.functions import Concat
from django.core.cache import cache

from metadata.models import ListEntry


def populate_values_list_cache(**kwargs):
    values = ListEntry.objects \
        .select_related('values_list') \
        .annotate(display=Concat(F('index'), V(' - '), F('value'))) \
        .order_by('values_list__index') \
        .values_list('values_list__index', 'index', 'display')

    grouped = {}
    for values_list, index, value in values:
        if values_list not in grouped:
            grouped[values_list] = []
        grouped[values_list].append((index, value))

    for list_index, list_entries in grouped.items():
        cache_key = 'values_list_{}'.format(list_index)
        cache.set(cache_key, list_entries)
