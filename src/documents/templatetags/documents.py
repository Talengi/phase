from django import template

from ..utils import stringify_value


register = template.Library()


HEADER_TPL = '<th id="%s" data-sortby="%s">%s <span class="%s"></span></th>'
SORT_MARKER_CLASS = 'glyphicon glyphicon-chevron-down'
TD_TPL = '<td class="column%s">{{%s}}</td>'


@register.simple_tag()
def generate_header_markup(document_class):
    """Generates the markup to be used in doc list table header."""
    columns = document_class.PhaseConfig.column_fields
    default_sort = document_class._meta.ordering[0]

    headers = list()
    for column in columns:
        headers.append(HEADER_TPL % (
            'column' + column[1],
            column[2],
            column[0],
            SORT_MARKER_CLASS if column[1] == default_sort else '',
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
