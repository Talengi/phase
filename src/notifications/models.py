# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from accounts.models import User


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('User'))
    title = models.CharField(
        _('Title'),
        max_length=64,
        null=True,
        blank=True)
    body = models.TextField(
        _('Body'),
        null=True,
        blank=True)
    created_on = models.DateTimeField(
        _('Created on'),
        default=timezone.now)
    seen = models.BooleanField(
        _('Seen'),
        default=False)

    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')


def notify(user, message):
    """Helper to notify a user.

    :arg user: can be a User instance or an user id

    """
    if isinstance(user, User):
        user = user.id
    notification = Notification.objects.create(user_id=user, body=message)
    return notification
