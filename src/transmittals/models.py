# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import logging
import shutil

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.core.urlresolvers import reverse

from model_utils import Choices

from documents.utils import save_document_forms
from documents.models import Document, Metadata, MetadataRevision
from reviews.models import CLASSES
from metadata.fields import ConfigurableChoiceField
from default_documents.validators import StringNumberValidator
from transmittals.fields import TransmittalFileField


logger = logging.getLogger(__name__)


class Transmittal(Metadata):
    """Transmittals are created when a contractor upload documents."""
    STATUSES = Choices(
        ('new', _('New')),
        ('invalid', _('Invalid')),
        ('tobechecked', _('To be checked')),
        ('rejected', _('Rejected')),
        ('processing', _('Processing')),
        ('accepted', _('Accepted')),
    )

    latest_revision = models.ForeignKey(
        'TransmittalRevision',
        verbose_name=_('Latest revision'))

    # General informations
    transmittal_date = models.DateField(
        _('Transmittal date'),
        null=True, blank=True)
    ack_of_receipt_date = models.DateField(
        _('Acknowledgment of receipt date'),
        null=True, blank=True)
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
    document_type = ConfigurableChoiceField(
        _('Document Type'),
        default="PID",
        max_length=3,
        list_index='DOCUMENT_TYPES')
    status = models.CharField(
        max_length=20,
        choices=STATUSES,
        default=STATUSES.tobechecked)
    created_on = models.DateField(
        _('Created on'),
        default=timezone.now)

    contractor = models.CharField(max_length=255)
    tobechecked_dir = models.CharField(max_length=255)
    accepted_dir = models.CharField(max_length=255)
    rejected_dir = models.CharField(max_length=255)

    class Meta:
        verbose_name = _('Transmittal')
        verbose_name_plural = _('Transmittals')
        index_together = (
            ('contract_number', 'originator', 'recipient', 'sequential_number',
             'status'),
        )

    class PhaseConfig:
        filter_fields = (
            'originator', 'recipient', 'status',
        )
        column_fields = (
            ('Reference', 'document_key'),
            ('Transmittal date', 'transmittal_date'),
            ('Ack. of receipt date', 'ack_of_receipt_date'),
            ('Originator', 'originator'),
            ('Recipient', 'recipient'),
            ('Document type', 'document_type'),
            ('Status', 'status'),
            ('Created on', 'created_on'),
        )
        searchable_fields = (
            'document_key',
            'originator',
            'recipient',
            'document_type',
            'status',
        )

    def __unicode__(self):
        return self.document_key

    @property
    def full_tobechecked_name(self):
        return os.path.join(self.tobechecked_dir, self.document_key)

    @property
    def full_accepted_name(self):
        return os.path.join(self.accepted_dir, self.document_key)

    @property
    def full_rejected_name(self):
        return os.path.join(self.rejected_dir, self.document_key)

    def generate_document_key(self):
        key = '{}-{}-{}-TRS-{:0>5d}'.format(
            self.contract_number,
            self.originator,
            self.recipient,
            self.sequential_number)
        return key

    @property
    def title(self):
        return self.document_key

    def get_absolute_url(self):
        return reverse('transmittal_diff', args=[self.pk, self.document_key])

    def reject(self):
        """Mark the transmittal as rejected.

        Upon rejecting the transmittal, we must perform the following
        operations:

          - update the transmittal status in db
          - move the corresponding files in the correct "refused" directory
          - send the notifications to the email list.

        """
        # Only transmittals with a pending validation can be refused
        if self.status != 'tobechecked':
            error_msg = 'The transmittal {} cannot be rejected ' \
                        'it it\'s current status ({})'.format(
                            self.document_key, self.status)
            raise RuntimeError(error_msg)

        # If an existing version already exists in rejected, we delete it before
        if os.path.exists(self.full_rejected_name):
            # Let's hope we got correct data and the process does not run
            # as root. We would do something that stupid anyway?
            logger.info('Deleteting directory {}'.format(self.full_rejected_name))
            shutil.rmtree(self.full_rejected_name)

        # Move to rejected directory
        if os.path.exists(self.full_tobechecked_name):
            try:
                os.rename(self.full_tobechecked_name, self.full_rejected_name)
            except OSError as e:
                logger.error('Cannot reject transmittal {} ({})'.format(
                    self, e))
                raise e
        else:
            # If the directory cannot be found in tobechecked, that's weird but we
            # won't trigger an error
            logger.warning('Transmittal {} files are gone'.format(self))

        self.status = 'rejected'
        self.save()

    def accept(self):
        """Starts the transmittal import process.

        Since the import can be quite long, we delegate the work to
        a celery task.

        """
        from transmittals.tasks import process_transmittal

        if self.status != 'tobechecked':
            error_msg = 'The transmittal {} cannot be accepted ' \
                        'in it\'s current state ({})'.format(
                            self.document_key, self.get_status_display())
            raise RuntimeError(error_msg)

        self.status = 'processing'
        self.save()

        process_transmittal.delay(self.pk)


class TransmittalRevision(MetadataRevision):
    status = ConfigurableChoiceField(
        _('Status'),
        max_length=20,
        list_index='STATUS_TRANSMITTALS')


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
    pdf_file = TransmittalFileField(
        verbose_name=_('Pdf file'))
    native_file = TransmittalFileField(
        verbose_name=_('Native file'),
        null=True, blank=True)

    class Meta:
        verbose_name = _('Trs Revision')
        verbose_name_plural = _('Trs Revisions')
        unique_together = ('transmittal', 'document_key', 'revision')

    def __unicode__(self):
        return '{} ({:02d})'.format(self.document_key, self.revision)

    def get_absolute_url(self):
        return reverse('transmittal_revision_diff', args=[
            self.transmittal.pk, self.transmittal.document_key,
            self.document_key, self.revision])

    def get_document_fields(self):
        """Return a dict of fields that will be passed to the document form.

        For now, this list is fixed.

        """
        fields = ('title', 'contract_number', 'originator', 'unit',
                  'discipline', 'document_type', 'sequential_number',
                  'docclass', 'revision', 'status')
        fields_dict = dict([(field, getattr(self, field)) for field in fields])

        files = ('pdf_file', 'native_file')
        files_dict = dict([(field, getattr(self, field)) for field in files])

        return fields_dict, files_dict

    def save_to_document(self):
        """Use self data to create / update the corresponding revision."""
        from default_documents.forms import (
            ContractorDeliverableForm, ContractorDeliverableRevisionForm)

        fields, files = self.get_document_fields()
        kwargs = {
            'data': fields,
            'files': files,
        }
        metadata = self.document.metadata
        kwargs.update({'instance': metadata})
        metadata_form = ContractorDeliverableForm(**kwargs)

        # If there is no such revision, the method will return None
        # which is fine.
        revision = metadata.get_revision(self.revision)

        # Let's make sure we are creating the revisions in the correct order.
        # This MUST have been enforced during the initial Transmittal validation.
        if revision is None:
            assert kwargs['data']['revision'] == metadata.latest_revision.revision + 1

        kwargs.update({'instance': revision})
        revision_form = ContractorDeliverableRevisionForm(**kwargs)

        save_document_forms(metadata_form, revision_form, self.document.category)
