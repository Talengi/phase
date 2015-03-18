# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.core.urlresolvers import reverse

from model_utils import Choices

from documents.models import Document
from reviews.models import CLASSES
from metadata.fields import ConfigurableChoiceField
from default_documents.validators import StringNumberValidator


class Transmittal(models.Model):
    """Transmittals are created when a contractor upload documents."""
    STATUSES = Choices(
        ('new', _('New')),
        ('invalid', _('Invalid')),
        ('tobechecked', _('To be checked')),
        ('rejected', _('Rejected')),
        ('accepted', _('Accepted')),
    )

    transmittal_key = models.SlugField(
        _('Transmittal key'),
        unique=True,
        db_index=True,
        max_length=250)
    contract_number = ConfigurableChoiceField(
        verbose_name='Contract Number',
        max_length=8,
        list_index='CONTRACT_NBS')
    originator = ConfigurableChoiceField(
        _('Originator'),
        default='CTR',
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
        default=STATUSES.tobechecked)
    created_on = models.DateField(
        _('Created on'),
        default=timezone.now)

    class Meta:
        verbose_name = _('Transmittal')
        verbose_name_plural = _('Transmittals')
        index_together = (
            ('contract_number', 'originator', 'recipient', 'sequential_number',
             'status'),
        )

    def __unicode__(self):
        return self.transmittal_key

    def save(self, *args, **kwargs):
        if not self.transmittal_key:
            self.transmittal_key = self.generate_key()
        super(Transmittal, self).save(*args, **kwargs)

    def generate_key(self):
        key = '{}-{}-{}-TRS-{:0>5d}'.format(
            self.contract_number,
            self.originator,
            self.recipient,
            self.sequential_number)
        return key

    def get_absolute_url(self):
        return reverse('transmittal_diff', args=[self.transmittal_key])

    def reject(self):
        """Mark the transmittal as rejected.

        Upon rejecting the transmittal, we must move the corresponding
        transmittal files in the correct "refused" directory.

        """
        # Only transmittals with a pending validation can be refused
        if self.status != 'tobechecked':
            raise RuntimeError('This transmittal cannot be rejected anymore')


class TrsRevision(models.Model):
    """Stores data imported from a single line in the csv."""
    transmittal = models.ForeignKey(
        Transmittal,
        verbose_name=_('Transmittal'))
    document = models.ForeignKey(
        Document,
        null=True, blank=True,
        verbose_name=_('Document'))
    document_key = models.SlugField(
        _('Document number'),
        max_length=250)
    title = models.TextField(
        verbose_name=_('Title'))
    revision = models.PositiveIntegerField(
        verbose_name=_('Revision'),
        default=1)
    accepted = models.NullBooleanField(
        verbose_name=_('Accepted?'))
    comment = models.TextField(
        verbose_name=_('Comment'),
        null=True, blank=True)
    is_new_revision = models.BooleanField(
        _('Is new revision?'))

    # Those are fields that will one day be configurable
    # but are static for now.
    contract_number = ConfigurableChoiceField(
        verbose_name='Contract Number',
        max_length=8,
        list_index='CONTRACT_NBS')
    originator = ConfigurableChoiceField(
        _('Originator'),
        default='FWF',
        max_length=3,
        list_index='ORIGINATORS')
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
    sequential_number = models.CharField(
        verbose_name=u"sequential Number",
        help_text=_('Select a four digit number'),
        default=u"0001",
        max_length=4,
        validators=[StringNumberValidator(4)])
    docclass = models.IntegerField(
        verbose_name=_('Class'),
        default=1,
        choices=CLASSES)
    status = ConfigurableChoiceField(
        verbose_name=_('Status'),
        default='STD',
        max_length=3,
        list_index='STATUSES',
        null=True, blank=True)

    class Meta:
        verbose_name = _('Trs Revision')
        verbose_name_plural = _('Trs Revisions')
        unique_together = ('transmittal', 'document_key', 'revision')

    def __unicode__(self):
        return '{} ({:02d})'.format(self.document_key, self.revision)

    def get_absolute_url(self):
        return reverse('transmittal_revision_diff', args=[
            self.transmittal.transmittal_key, self.document_key, self.revision])
