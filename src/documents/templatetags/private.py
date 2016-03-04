# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os

from django import template
from django.core.urlresolvers import reverse


register = template.Library()


@register.simple_tag
def private_link(file_field):
    if not file_field:
        return 'ND'

    relative_name = file_field.name
    basename = os.path.basename(relative_name)
    url = reverse('protected_download', args=[relative_name])
    return '<a href="{}">{}</a>'.format(
        url, basename)


def get_download_link(revision, fieldname, make_short=False):
    """Used by following tags to get an html link. If `make_short` is set
    to True, it limits anchor name to 10 characters and display a
    bootstrap tooltip."""
    field = getattr(revision, fieldname)
    if not field:
        return ''

    url = reverse('revision_file_download', args=[
        revision.document.category.organisation.slug,
        revision.document.category.slug,
        revision.document.document_key,
        revision.revision,
        fieldname
    ])
    file_path = os.path.basename(field.name)

    tpl = '<a href="{0}">{1}</a>'
    if len(file_path) > 10 and make_short:
        tpl = '<a data-toggle="tooltip" data-placement="left" ' \
            'href="{0}" title="{1}" >{1:.10}…</a>'

    return tpl.format(url, file_path)


@register.simple_tag
def download_link(revision, fieldname):
    return get_download_link(revision, fieldname)


@register.simple_tag
def short_download_link(revision, fieldname):
    return get_download_link(revision, fieldname, make_short=True)
