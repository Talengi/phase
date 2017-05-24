

from django import template
from django.utils.html import format_html


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

    return format_html('<span class="glyphicon glyphicon-{}"></span>', icon)
