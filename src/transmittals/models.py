# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import logging
import shutil
import uuid
import zipfile
import tempfile
import datetime
from collections import OrderedDict

from django import forms
from django.db import models, transaction
from django.db.models import Case, Value, When
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.core.files.base import ContentFile
from django.utils import timezone

from model_utils import Choices
from elasticsearch_dsl import F

from documents.utils import save_document_forms
from documents.models import Document, Metadata, MetadataRevision
from documents.templatetags.documents import MenuItem
from reviews.models import CLASSES, ReviewMixin
from search.utils import build_index_data, bulk_actions
from metadata.fields import ConfigurableChoiceField
from default_documents.validators import StringNumberValidator
from privatemedia.fields import ProtectedFileField, PrivateFileField
from transmittals.fields import TransmittalFileField
from transmittals.fileutils import file_transmitted_file_path
from transmittals.pdf import transmittal_to_pdf


logger = logging.getLogger(__name__)


class Transmittal(Metadata):
    """Represents and incoming transmittal.

    Transmittals are created when a contractor upload documents.

    """
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

    transmittal_key = models.CharField(
        _('Transmittal key'),
        max_length=250)

    # General informations
    transmittal_date = models.DateField(
        _('Transmittal date'),
        null=True, blank=True)
    ack_of_receipt_date = models.DateField(
        _('Acknowledgment of receipt date'),
        null=True, blank=True)
    # We'll keep it for a while
    contract_number_old = ConfigurableChoiceField(
        verbose_name='Contract Number',
        max_length=8,
        list_index='CONTRACT_NBS',
        null=True,
        blank=True)
    contract_number = models.CharField(
        verbose_name='Contract Number',
        max_length=50)
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
        _('sequential number'),
        null=True, blank=True)
    document_type = ConfigurableChoiceField(
        _('Document Type'),
        default="PID",
        max_length=3,
        list_index='DOCUMENT_TYPES')
    status = models.CharField(
        max_length=20,
        choices=STATUSES,
        default=STATUSES.tobechecked)

    # Related documents
    related_documents = models.ManyToManyField(
        'documents.Document',
        related_name='transmittals_related_set',
        blank=True)

    contractor = models.CharField(max_length=255, null=True, blank=True)
    tobechecked_dir = models.CharField(max_length=255, null=True, blank=True)
    accepted_dir = models.CharField(max_length=255, null=True, blank=True)
    rejected_dir = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        app_label = 'transmittals'
        ordering = ('document_number',)
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
            ('Reference', 'document_number'),
            ('Transmittal date', 'transmittal_date'),
            ('Acknowledgment of receipt', 'ack_of_receipt_date'),
            ('Originator', 'originator'),
            ('Recipient', 'recipient'),
            ('Document type', 'document_type'),
            ('Status', 'status'),
        )

    def __unicode__(self):
        return self.document_key

    def save(self, *args, **kwargs):
        if not self.transmittal_key:
            if not self.document_key:
                self.document_key = self.generate_document_key()
            self.transmittal_key = self.document_key
        super(Transmittal, self).save(*args, **kwargs)

    @property
    def full_tobechecked_name(self):
        return os.path.join(self.tobechecked_dir, self.transmittal_key)

    @property
    def full_accepted_name(self):
        return os.path.join(self.accepted_dir, self.transmittal_key)

    @property
    def full_rejected_name(self):
        return os.path.join(self.rejected_dir, self.transmittal_key)

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

    @transaction.atomic
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
            # as root. Who would do something that stupid anyway?
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

        # Since the document_key "unique" constraint is enforced in the parent
        # class (Metadata), we need to update this object's key to allow a
        # new transmittal submission with the same transmittal key.
        new_key = '{}-{}'.format(
            self.document_key,
            uuid.uuid4())

        self.document_key = new_key
        self.status = 'rejected'
        self.save()

        self.document.document_key = new_key
        self.document.save()

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
    trs_status = ConfigurableChoiceField(
        _('Status'),
        max_length=20,
        default='opened',
        list_index='STATUS_TRANSMITTALS')

    class Meta:
        app_label = 'transmittals'


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
    category = models.ForeignKey('categories.Category')
    title = models.TextField(
        verbose_name=_('Title'))
    revision = models.PositiveIntegerField(
        verbose_name=_('Revision'),
        default=0)
    revision_date = models.DateField(
        _('Revision date'),
        null=True, blank=True)
    received_date = models.DateField(
        _('Received date'),
        null=True, blank=True)
    created_on = models.DateField(
        _('Created on'),
        null=True, blank=True)
    accepted = models.NullBooleanField(
        verbose_name=_('Accepted?'))
    comment = models.TextField(
        verbose_name=_('Comment'),
        null=True, blank=True)
    is_new_revision = models.BooleanField(
        _('Is new revision?'))

    # We'll keep it for a while.
    # Those are fields that will one day be configurable
    # but are static for now.
    contract_number_old = ConfigurableChoiceField(
        verbose_name='Contract Number',
        max_length=8,
        list_index='CONTRACT_NBS',
        null=True,
        blank=True)
    contract_number = models.CharField(
        verbose_name='Contract Number',
        max_length=50)
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
        validators=[StringNumberValidator(4)],
        null=True, blank=True)
    system = ConfigurableChoiceField(
        _('System'),
        list_index='SYSTEMS',
        null=True, blank=True)
    wbs = ConfigurableChoiceField(
        _('Wbs'),
        max_length=20,
        list_index='WBS',
        null=True, blank=True)
    weight = models.IntegerField(
        _('Weight'),
        null=True, blank=True)
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
    return_code = models.PositiveIntegerField(
        _('Return code'),
        null=True, blank=True)
    review_start_date = models.DateField(
        _('Review start date'),
        null=True, blank=True)
    review_due_date = models.DateField(
        _('Review due date'),
        null=True, blank=True)
    review_leader = models.CharField(
        _('Review leader'),
        max_length=150,
        null=True, blank=True)
    leader_comment_date = models.DateField(
        _('Leader comment date'),
        null=True, blank=True)
    review_approver = models.CharField(
        _('Review approver'),
        max_length=150,
        null=True, blank=True)
    approver_comment_date = models.DateField(
        _('Approver comment date'),
        null=True, blank=True)
    review_trs = models.CharField(
        verbose_name=_('Review transmittal name'),
        max_length=255,
        null=True, blank=True)
    review_trs_status = models.CharField(
        verbose_name=_('Review transmittal status'),
        max_length=50,
        null=True, blank=True)
    outgoing_trs = models.CharField(
        verbose_name=_('Outgoing transmittal name'),
        max_length=255,
        null=True, blank=True)
    outgoing_trs_status = models.CharField(
        verbose_name=_('Outgoing transmittal status'),
        max_length=50,
        null=True, blank=True)
    outgoing_trs_sent_date = models.DateField(
        verbose_name=_('Outgoing transmittal sent date'),
        null=True, blank=True)
    doc_category = models.CharField(
        max_length=50,
        verbose_name=_('Doc category'))
    pdf_file = TransmittalFileField(
        verbose_name=_('Pdf file'))
    native_file = TransmittalFileField(
        verbose_name=_('Native file'),
        null=True, blank=True, max_length=255)

    class Meta:
        app_label = 'transmittals'
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
        """Return a dict of fields that will be passed to the document form."""
        columns = self.category.get_transmittal_columns()
        fields = columns.values()
        fields_dict = dict([(field, getattr(self, field)) for field in fields])

        # XXX
        # This is a HACK
        fields_dict.update({
            'sequential_number': '{:04}'.format(int(self.sequential_number))
        })

        files_dict = {
            'native_file': self.native_file,
            'pdf_file': self.pdf_file}

        return fields_dict, files_dict

    def save_to_document(self):
        """Use self data to create / update the corresponding revision."""

        fields, files = self.get_document_fields()
        kwargs = {
            'category': self.category,
            'data': fields,
            'files': files
        }

        # The document was created earlier during
        # the batch import
        if self.document is None and self.revision > 0:
            self.document = Document.objects.get(document_key=self.document_key)

        metadata = getattr(self.document, 'metadata', None)
        kwargs.update({'instance': metadata})
        Form = self.category.get_metadata_form_class()
        metadata_form = Form(**kwargs)

        # If there is no such revision, the method will return None
        # which is fine.
        revision = metadata.get_revision(self.revision) if metadata else None

        kwargs.update({'instance': revision})
        RevisionForm = self.category.get_revision_form_class()
        revision_form = RevisionForm(**kwargs)

        doc, meta, rev = save_document_forms(
            metadata_form, revision_form, self.category)

        # Performs custom import action
        rev.post_trs_import(self)


class OutgoingTransmittal(Metadata):
    """Represents an outgoing transmittal.

    In the end, Transmittal and OutgoingTransmittal should be refactored into a
    single class. However, the incoming trs class contains too much specific
    code and is kept isolated for now.

    """
    EXTERNAL_REVIEW_DURATION = 13

    latest_revision = models.ForeignKey(
        'OutgoingTransmittalRevision',
        verbose_name=_('Latest revision'))

    revisions_category = models.ForeignKey(
        'categories.Category',
        verbose_name=_('From category'),
        on_delete=models.PROTECT)
    # We'll have to delete it, but let's keep this one for a while
    contract_number_old = ConfigurableChoiceField(
        verbose_name='Contract Number',
        max_length=8,
        list_index='CONTRACT_NBS',
        null=True,
        blank=True
    )
    contract_number = models.CharField(
        verbose_name='Contract Number',
        max_length=50)
    originator = models.CharField(
        _('Originator'),
        max_length=3)
    recipient = models.ForeignKey(
        'accounts.Entity',
        verbose_name=_('Recipient'))
    sequential_number = models.PositiveIntegerField(
        _('sequential number'),
        null=True, blank=True)
    ack_of_receipt_date = models.DateField(
        _('Acknowledgment of receipt date'),
        null=True, blank=True)
    ack_of_receipt_author = models.ForeignKey(
        'accounts.User',
        verbose_name=_('Acknowledgment of receipt author'),
        null=True, blank=True,
        on_delete=models.PROTECT)

    class Meta:
        app_label = 'transmittals'
        ordering = ('document_number',)
        verbose_name = _('Outgoing transmittal')
        verbose_name_plural = _('Outgoing transmittals')

    class PhaseConfig:
        filter_fields = ('recipient', 'ack_of_receipt')
        custom_filters = OrderedDict((
            ('has_errors', {
                'field': forms.ChoiceField,
                'field_kwargs': {
                    'choices': (
                        ('', '----------'),
                        ('true', 'Yes'),
                        ('false', 'No'),
                    )
                },
                'label': _('Has errors?'),
                'filters': {
                    '': None,
                    'true': F('term', has_error=True),
                    'false': F('term', has_error=False)
                }
            }),)
        )
        column_fields = (
            ('Reference', 'document_number'),
            ('Created', 'created_on'),
            ('Originator', 'originator'),
            ('Recipient', 'recipient'),
            ('Acknowledgment of receipt', 'ack_of_receipt'),
            ('Has error', 'has_error'),
        )
        export_fields = OrderedDict((
            ('Document number', 'document_number'),
            ('Contract Number', 'contract_number'),
            ('Originator', 'originator'),
            ('Recipient', 'recipient'),
            ('Ack. of receipt', 'ack_of_receipt'),
            ('Ack. of receipt date', 'ack_of_receipt_date'),
            ('Ack. of receipt author', 'ack_of_receipt_author'),
            ('Revision', 'revision_name'),
            ('Received date', 'received_date'),
            ('Has error', 'has_error'),
        ))

    def __unicode__(self):
        return self.document_key

    def get_revisions(self):
        _class = self.get_revisions_class()
        revisions = _class.objects.filter(transmittal=self).select_related()
        return revisions

    def get_revisions_class(self):
        return self.revisions_category.revision_class()

    @property
    def ack_of_receipt(self):
        return bool(self.ack_of_receipt_date)

    def get_ack_of_receipt_display(self):
        return 'Yes' if self.ack_of_receipt else 'No'
    get_ack_of_receipt_display.short_description = 'Acknowledgment of receipt'

    def generate_document_key(self):
        key = '{}-{}-{}-TRS-{:0>5d}'.format(
            self.contract_number,
            self.originator,
            self.recipient.trigram,
            self.sequential_number)
        return key

    @property
    def title(self):
        return self.document_key

    @classmethod
    def get_document_download_form(cls, data, queryset):
        from transmittals.forms import TransmittalDownloadForm
        return TransmittalDownloadForm(data, queryset=queryset)

    @classmethod
    def compress_documents(cls, documents, **kwargs):
        """See `documents.models.Metadata.compress_documents`"""
        content = kwargs.get('content', 'transmittal')
        revisions = kwargs.get('revisions', 'latest')

        temp_file = tempfile.TemporaryFile()

        with zipfile.ZipFile(temp_file, mode='w') as zip_file:
            for document in documents:
                dirname = document.document_key
                revision = document.get_latest_revision()

                # Should we embed the transmittal pdf?
                if content in ('transmittal', 'both'):

                    # All revisions or just the latest?
                    if revisions == 'latest':
                        revs = [revision]
                    elif revisions == 'all':
                        revs = document.get_all_revisions()

                    # Embed the file in the zip archive
                    for rev in revs:
                        pdf_file = rev.pdf_file
                        pdf_basename = os.path.basename(pdf_file.name)

                        # Avoiding to break export process
                        if not pdf_file:
                            continue

                        # If file is gone, don't break export process
                        try:
                            zip_file.write(
                                pdf_file.path,
                                '{}/{}'.format(dirname, pdf_basename),
                                compress_type=zipfile.ZIP_DEFLATED)
                        except OSError:
                            logger.warning(
                                'File: {} missing in export process'.format(pdf_file))

                # Should we embed review comments?
                if content in ('revisions', 'both'):
                    meta = document.get_metadata()
                    exported_revs = meta.get_revisions()
                    for rev in exported_revs:
                        if rev.file_transmitted:
                            comments_file = rev.file_transmitted
                            comments_basename = os.path.basename(comments_file.path)
                            zip_file.write(
                                comments_file.path,
                                '{}/{}/{}'.format(
                                    dirname,
                                    rev.document.document_key,
                                    comments_basename),
                                compress_type=zipfile.ZIP_DEFLATED)

        return temp_file

    def link_to_revisions(self, revisions):
        """Set the given revisions as related documents.

        The revisions MUST be valid:
         - belong to the same category
         - be transmittable objects

        """
        ids = []
        index_data = []
        for revision in revisions:
            ids.append(revision.id)

            # Update ES index to make sure the "can_be_transmitted"
            # filter is up to date
            index_datum = build_index_data(revision)
            index_datum['_source']['can_be_transmitted'] = False
            index_data.append(index_datum)

        with transaction.atomic():
            today = timezone.now()
            later = today + datetime.timedelta(days=self.EXTERNAL_REVIEW_DURATION)

            # Mark revisions as transmitted
            Revision = type(revisions[0])
            Revision.objects \
                .filter(id__in=ids) \
                .update(
                    transmittal=self,
                    transmittal_sent_date=timezone.now(),
                    external_review_due_date=Case(
                        When(purpose_of_issue='FR', then=Value(later)),
                        When(purpose_of_issue='FI', then=Value(None)),
                    ))

            bulk_actions(index_data)

    @classmethod
    def get_batch_actions(cls, category, user):
        actions = super(OutgoingTransmittal, cls).get_batch_actions(
            category, user)

        if user.is_external:
            actions['ack_transmittals'] = MenuItem(
                'ack-transmittals',
                _('Ack receipt'),
                reverse('transmittal_batch_ack_of_receipt', args=[
                    category.organisation.slug,
                    category.slug]),
                ajax=False,
                icon='eye-open',
            )

        return actions

    @classmethod
    def get_batch_actions_modals(cls):
        """Returns a list of templates used in batch actions."""
        return ['transmittals/document_list_download_modal.html']

    def ack_receipt(self, user, save=True):
        """Acknowledge receipt of this transmittal."""
        self.ack_of_receipt_date = timezone.now().date()
        self.ack_of_receipt_author = user

        if save:
            self.save()


class OutgoingTransmittalRevision(MetadataRevision):
    error_msg = models.TextField(
        _('Error message'),
        help_text=_('Report an error to the DC'),
        null=True, blank=True)
    error_notified = models.BooleanField(
        _('Was error already notified?'),
        default=False)

    class Meta:
        app_label = 'transmittals'

    def get_initial_empty(self):
        empty_fields = super(OutgoingTransmittalRevision, self).get_initial_empty()
        return empty_fields + (
            'error_msg',
        )

    def has_error(self):
        return bool(self.error_msg)
    has_error.short_description = _('Has error')

    def generate_pdf_file(self):
        pdf_content = transmittal_to_pdf(self)
        pdf_file = ContentFile(pdf_content)
        return pdf_file

    def get_actions(self, metadata, user):
        actions = super(OutgoingTransmittalRevision, self).get_actions(
            metadata, user)
        category = self.document.category

        if user.is_external and metadata.ack_of_receipt_date is None:
            actions.insert(-3, MenuItem(
                'ack-transmittal',
                _('Acknowledge receipt'),
                reverse('transmittal_ack_of_receipt', args=[
                    category.organisation.slug,
                    category.slug,
                    self.document.document_key])
            ))

        return actions


class ExportedRevision(models.Model):
    """Link between an outgoing transmittal and an exported document."""
    document = models.ForeignKey(Document)
    transmittal = models.ForeignKey(OutgoingTransmittal)
    revision = models.PositiveIntegerField(_('Revision'))
    title = models.TextField(_('Title'))
    status = models.CharField(_('Status'), max_length=5)
    return_code = models.CharField(_('Return code'), max_length=5)
    comments = ProtectedFileField(
        _('Comments'),
        null=True, blank=True)

    class Meta:
        verbose_name = _('Exported revision')
        verbose_name_plural = _('Exported revisions')
        app_label = 'transmittals'

    @property
    def name(self):
        """A revision identifier should be displayed with two digits"""
        return u'%02d' % self.revision


class TransmittableMixin(ReviewMixin):
    """Define behavior of revisions that can be embedded in transmittals.

    Only reviewable documents can be transmitted, hence the mixin
    inheritance.

    """

    PURPOSE_OF_ISSUE_CHOICES = Choices(
        ('FR', _('For review')),
        ('FI', _('For information')))

    transmittal = models.ForeignKey(
        'OutgoingTransmittal',
        verbose_name='transmittal',
        null=True, blank=True,
        on_delete=models.SET_NULL)
    transmittal_sent_date = models.DateField(
        _('Transmittal sent date'),
        null=True, blank=True)
    trs_return_code = ConfigurableChoiceField(
        _('Final return code'),
        max_length=3,
        null=True, blank=True,
        list_index='REVIEW_RETURN_CODES')
    file_transmitted = PrivateFileField(
        _('File Transmitted'),
        null=True, blank=True,
        upload_to=file_transmitted_file_path)
    under_preparation_by = models.ForeignKey(
        'accounts.User',
        verbose_name=_('Under preparation by'),
        related_name='+',
        null=True, blank=True)
    internal_review = models.BooleanField(
        _('Internal review only?'),
        choices=Choices(
            (False, 'No'),
            (True, 'Yes')
        ),
        default=False)
    purpose_of_issue = models.CharField(
        _('Purpose of issue'),
        max_length=2,
        blank=True,
        choices=PURPOSE_OF_ISSUE_CHOICES,
        default=PURPOSE_OF_ISSUE_CHOICES.FR)
    external_review_due_date = models.DateField(
        _('External due date'),
        null=True, blank=True)

    class Meta:
        abstract = True

    def get_final_return_code(self):
        """Returns the latest available return code."""
        if self.trs_return_code:
            rc = self.trs_return_code
        elif hasattr(self, 'return_code'):
            rc = self.return_code
        else:
            rc = ''
        return rc

    @property
    def can_be_reviewed(self):
        """Can this revision be reviewed.

        A revision that was already embedded in a transmittal cannot
        be reviewed anymore.

        """
        # Turns out, simply calling "self.can_be_transmitted" leads to
        # an infinite recursion error.
        return all((
            super(TransmittableMixin, self).can_be_reviewed,
            not self.transmittal))

    @property
    def can_be_transmitted(self):
        """Is this rev ready to be embedded in an outgoing trs?"""
        return all((
            not self.internal_review,
            not self.transmittal,
            self.document.current_revision == self.revision))

    def get_initial_empty(self):
        """New revision initial data that must be empty."""
        empty_fields = super(TransmittableMixin, self).get_initial_empty()
        return empty_fields + (
            'trs_return_code',
            'file_transmitted',
            'external_review_due_date',
        )
