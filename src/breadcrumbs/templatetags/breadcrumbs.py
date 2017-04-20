from __future__ import unicode_literals

from django import template
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def crumb(obj):
    if obj:
        if hasattr(obj, 'get_absolute_url'):
            url = obj.get_absolute_url()
        elif isinstance(obj, (list, tuple)):
            obj, url = obj
        else:
            url = '#'
        if url != '#':
            ret = format_html('<li><a href="{}">{}</a></li>&nbsp;', url, obj)
        else:
            ret = format_html('<li><span>{}</span></li>&nbsp;', obj)
    else:
        ret = ''
    return ret
