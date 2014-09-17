from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class Message(models.Model):
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
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')


def notify(user, message):
    message = Message.objects.create(user=user, body=message)
    return message
