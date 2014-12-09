# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from documents.models import Document


class Note(models.Model):
    """A single message in a single thread discussion."""
    document = models.ForeignKey(
        Document,
        verbose_name=_('Document'))
    revision = models.PositiveIntegerField(
        _('Revision'))
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Author'))
    body = models.TextField(
        _('Body'))
    created_on = models.DateTimeField(
        _('Created on'),
        default=timezone.now)

    class Meta:
        verbose_name = _('Note')
        verbose_name_plural = _('Notes')
