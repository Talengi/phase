from __future__ import unicode_literals

from django import template

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
            ret = '<li><a href="{}">{}</a></li>&nbsp;'.format(url, obj)
        else:
            ret = '<li><span>{}</span></li>&nbsp;'.format(obj)
    else:
        ret = ''
    return ret
