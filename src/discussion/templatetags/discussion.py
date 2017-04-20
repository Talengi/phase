# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django import template
from django.utils.html import format_html

from discussion.utils import get_discussion_length


register = template.Library()


@register.simple_tag
def discussion_length(revision):
    length = get_discussion_length(revision)
    return length


@register.simple_tag
def discussion_length_badge(revision):
    length = get_discussion_length(revision)
    return format_html('<span class="badge">{}</span>', length)
