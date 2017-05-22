from django import template
from django.utils.html import format_html_join
from crispy_forms.layout import Fieldset


register = template.Library()


@register.simple_tag
def crispy_menu(form, helper):
    menu = ''

    if hasattr(helper, 'layout') and helper.layout:
        fields = [field for field in helper.layout.fields if isinstance(field, Fieldset)]

        menu = format_html_join(
            ' ',
            '<li><a href="#{}">{}</a></li>',
            ((field.css_id, str(field.legend)) for field in fields)
        )

    return menu
