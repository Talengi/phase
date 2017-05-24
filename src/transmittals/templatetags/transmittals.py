# -*- coding: utf-8 -*-



from django import template
from django.contrib.contenttypes.models import ContentType
from django.utils.html import format_html

from transmittals.models import OutgoingTransmittal
from categories.models import Category


register = template.Library()


@register.simple_tag(takes_context=True)
def diffclass(context, variable):
    revision = context['revision']
    trs_revision = context['trs_revision']

    if getattr(revision, variable) != getattr(trs_revision, variable):
        return 'warning'
    else:
        return ''


@register.simple_tag
def isnew_label(trs_revision):
    if trs_revision.is_new_revision:
        label_class = 'warning'
        label_text = 'New'
    else:
        label_class = 'primary'
        label_text = 'Updated'

    return format_html(
        '<span class="label label-{}">{}</span>', label_class, label_text)


@register.assignment_tag
def get_outgoing_transmittal_categories(organisation_slug=None):
    """Return categories with an "OutgoingTransmittal" content type"""
    ct = ContentType.objects.get_for_model(OutgoingTransmittal)
    categories = Category.objects \
        .select_related() \
        .filter(category_template__metadata_model=ct) \
        .prefetch_related('third_parties')

    if organisation_slug:
        categories = categories.filter(organisation__slug=organisation_slug)

    return categories
