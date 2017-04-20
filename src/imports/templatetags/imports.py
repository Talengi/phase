import json

from django import template
from django.utils.html import format_html


register = template.Library()


@register.simple_tag
def errors_to_list(json_data):
    """Takes a json encoded dict and returns html"""
    if json_data:
        data = json.loads(json_data)
        data = [(k, v[0]) for k, v in data.items()]
        data_list = ''.join(['<dt>%s</dt><dd>%s</dd>' % (k, v) for k, v in data])
        return format_html('<dl>{}</dl>', data_list)
    else:
        return ''
