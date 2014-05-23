from __future__ import unicode_literals

from django import template


register = template.Library()


@register.simple_tag
def notification_icon(tag):
    icons = {
        'info': 'info-sign',
        'success': 'ok-sign',
        'warning': 'question-sign',
        'error': 'exclamation-sign',
    }
    icon = icons.get(tag, '')

    return '<span class="glyphicon glyphicon-{}"></span>'.format(icon)
