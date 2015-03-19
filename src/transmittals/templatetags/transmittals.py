# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import template


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

    return '<span class="label label-{}">{}</span>'.format(
        label_class, label_text)
