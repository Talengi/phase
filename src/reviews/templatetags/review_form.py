# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django import template
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import filesizeformat
from django.utils.html import format_html


register = template.Library()


@register.simple_tag
def file_link(file, name=None):
    if file:
        name = name if name else os.path.basename(file.name)
        link = format_html(
            '<a href="{}">{}</a> ({})',
            file.url,
            name,
            filesizeformat(file.size))
    else:
        link = ''
    return link


@register.filter
def na_if_none(data):
    return data if data else _('N/A')
