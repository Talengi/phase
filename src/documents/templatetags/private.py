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
