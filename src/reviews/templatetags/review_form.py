from django import template
from django.utils.translation import ugettext_lazy as _


register = template.Library()


@register.simple_tag
def file_link(file, name=None):
    name = name if name else file
    if file:
        link = '<a href="%s">%s</a>' % (file.url, name)
    else:
        link = ''
    return link


@register.filter
def na_if_none(data):
    return data if data else _('N/A')
