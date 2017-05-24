# -*- coding: utf-8 -*-


from django import template
from django.core.cache import cache


register = template.Library()


@register.assignment_tag
def get_values_list(list_index):
    """Return a values list from cache."""
    cache_key = 'values_list_{}'.format(list_index)
    values = cache.get(cache_key)
    return values
