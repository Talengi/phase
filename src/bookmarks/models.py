# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from accounts.models import User


class Bookmark(models.Model):
    """A simple link stored in db."""
    user = models.ForeignKey(User)
    url = models.UrlField(_('Url'))
    created_on = models.DateField(
        _('Created on'),
        default=timezone.now)

    class Meta:
        verbose_name = _('Bookmark')
        verbose_name_plural = _('Bookmarks')
