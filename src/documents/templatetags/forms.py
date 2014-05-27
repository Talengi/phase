from django import template
from django.forms.widgets import FileInput


register = template.Library()


@register.filter
def is_input_file(field):
    widget = field.field.widget
    return isinstance(widget, FileInput)
