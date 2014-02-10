from django import template
from crispy_forms.layout import Fieldset


register = template.Library()


@register.simple_tag
def crispy_menu(form, helper):
    menu = []

    if hasattr(helper, 'layout') and helper.layout:
        fields = [field for field in helper.layout.fields if isinstance(field, Fieldset)]

        for field in fields:
            menu.append('<li><a href="#%s">%s</a></li>' % (
                field.css_id,
                unicode(field.legend)
            ))

    return ' '.join(menu)
