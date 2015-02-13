# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from model_utils import Choices

from documents.models import Document
from documents.reviews import CLASSES
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


class TrsRevision(models.Model):
    """Stores data imported from a single line in the csv."""
    STATUSES = Choices(
        'new',
        'accepted',
        'refused',
    )

    document = models.ForeignKey(
        Document,
        verbose_name=_('Document'))
    title = models.TextField(
        verbose_name=_('Title'))
    revision = models.PositiveIntegerField(
        verbose_name=_('Revision'),
        default=1)
    status = models.CharField(
        max_length=20,
        choices=STATUSES,
        default=STATUSES.new)
    is_new_revision = models.BooleanField(
        _('Is new revision?'))

    # Those are fields that will one day be configurable
    # but are static for now.
    revision_status = ConfigurableChoiceField(
        verbose_name=_('Status'),
        default='STD',
        max_length=3,
        list_index='STATUSES',
        null=True, blank=True)
    docclass = models.IntegerField(
        verbose_name=_('Class'),
        default=1,
        choices=CLASSES)
    unit = ConfigurableChoiceField(
        verbose_name=_('Unit'),
        default='000',
        max_length=3,
        list_index='UNITS')
    discipline = ConfigurableChoiceField(
        verbose_name=_('Discipline'),
        default='PCS',
        max_length=3,
        list_index='DISCIPLINES')
    document_type = ConfigurableChoiceField(
        verbose_name=_('Document Type'),
        default='PID',
        max_length=3,
        list_index='DOCUMENT_TYPES')

    class Meta:
        verbose_name = _('Trs Revision')
        verbose_name_plural = _('Trs Revisions')
