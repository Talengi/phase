from django import template

from ..utils import stringify_value


register = template.Library()


HEADER_TPL = '<th id="column%s" data-sortby="%s">%s</th>'
TD_TPL = '<td class="column%s"><%%= %s %%></td>'


@register.simple_tag()
def generate_header_markup(document_class):
    """Generates the markup to be used in doc list table header."""
    columns = document_class.PhaseConfig.column_fields

    headers = list()
    for column in columns:
        headers.append(HEADER_TPL % (
            column[1],
            column[1],
            column[0],
        ))

    return ' '.join(headers)


@register.simple_tag()
def generate_template_markup(document_class):
    """Generates the markup to be used in doc list table rows."""
    columns = document_class.PhaseConfig.column_fields

    tds = list()
    for column in columns:
        tds.append(TD_TPL % (
            column[1],
            column[1],
        ))

    return ' '.join(tds)


@register.filter
def stringify(val):
    return stringify_value(val)
