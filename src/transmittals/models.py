# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from model_utils import Choices

from metadata.fields import ConfigurableChoiceField


class Transmittal(models.Model):
    """Transmittals are created when a contractor upload documents."""
    STATUSES = Choices(
        'new',
        'invalid',
        'tobechecked',
        'rejected',
        'accepted',
    )

    contract_number = ConfigurableChoiceField(
        verbose_name='Contract Number',
        max_length=8,
        list_index='CONTRACT_NBS')
    originator = ConfigurableChoiceField(
        _('Originator'),
        default='FWF',
        max_length=3,
        list_index='ORIGINATORS')
    recipient = ConfigurableChoiceField(
        _('Recipient'),
        max_length=50,
        list_index='RECIPIENTS')
    sequential_number = models.PositiveIntegerField(
        _('sequential number'))
    status = models.CharField(
        max_length=20,
        choices=STATUSES,
        default=STATUSES.new)
    created_on = models.DateField(
        _('Created on'),
        default=timezone.now)

    class Meta:
        verbose_name = _('Transmittal')
        verbose_name_plural = _('Transmittals')

    @property
    def name(self):
        return '{}_{}_{}_TRS_{:0>5d}' % (
            self.contract_number,
            self.originator,
            self.recipient,
            self.sequential_number)
