# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone


class Export(models.Model):
    """Represents a document export request."""
    owner = models.ForeignKey(
        'accounts.User',
        verbose_name=_('Owner'))
    category = models.ForeignKey(
        'categories.Category',
        verbose_name=_('Category'))
    querystring = models.TextField(
        _('Querystring'),
        help_text=_('The search filter querystring'))
    created_on = models.DateTimeField(
        _('Created on'),
        default=timezone.now)

    class Meta:
        app_label = 'exports'
        verbose_name = _('Export')
        verbose_name_plural = _('Exports')
