# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.core.cache import cache

from accounts.models import User


class Bookmark(models.Model):
    """A simple link stored in db."""
    user = models.ForeignKey(User)
    name = models.CharField(
        _('Name'),
        max_length=50)
    url = models.CharField(
        _('Url'),
        max_length=200)
    created_on = models.DateField(
        _('Created on'),
        default=timezone.now)

    class Meta:
        verbose_name = _('Bookmark')
        verbose_name_plural = _('Bookmarks')

    def save(self, *args, **kwargs):
        super(Bookmark, self).save(*args, **kwargs)
        self.clear_cache()

    def delete(self, *args, **kwargs):
        super(Bookmark, self).delete(*args, **kwargs)
        self.clear_cache()

    def clear_cache(self):
        """Clear query cache for the given user."""
        cache_key = 'bookmarks_%d' % self.user_id
        cache.delete(cache_key)
