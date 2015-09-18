# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import OrderedDict

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django import forms

from elasticsearch_dsl import F

from metadata.fields import ConfigurableChoiceField
from accounts.models import User
from reviews.models import ReviewMixin
from documents.models import Metadata, MetadataRevision
from documents.constants import BOOLEANS
from .validators import StringNumberValidator


class ContractorDeliverable(Metadata):
    latest_revision = models.ForeignKey(
        'ContractorDeliverableRevision',
        verbose_name=_('Latest revision'))

    # General information
    title = models.TextField(
        verbose_name=u"Title")
    contract_number = ConfigurableChoiceField(
        verbose_name=u"Contract Number",
        max_length=15,
        list_index='CONTRACT_NBS')
    originator = ConfigurableChoiceField(
        verbose_name=u"Originator",
        default=u"FWF",
        max_length=3,
        list_index='ORIGINATORS')
    unit = ConfigurableChoiceField(
        verbose_name=u"Unit",
        default="000",
        max_length=3,
        list_index='UNITS')
    discipline = ConfigurableChoiceField(
        verbose_name=u"Discipline",
        default="PCS",
        max_length=3,
        list_index='DISCIPLINES')
    document_type = ConfigurableChoiceField(
        verbose_name=u"Document Type",
        default="PID",
        max_length=3,
        list_index='DOCUMENT_TYPES')
    sequential_number = models.CharField(
        verbose_name=u"sequential Number",
        help_text=_('Select a four digit number'),
        default=u"0001",
        max_length=4,
        validators=[StringNumberValidator(4)])
    system = ConfigurableChoiceField(
        verbose_name=u"System",
        list_index='SYSTEMS',
        null=True, blank=True)
    wbs = ConfigurableChoiceField(
        verbose_name=u"WBS",
        max_length=20,
        list_index='WBS',
        null=True, blank=True)
    weight = models.IntegerField(
        verbose_name=u"Weight",
        null=True, blank=True)

    # Related documents
    related_documents = models.ManyToManyField(
        'documents.Document',
        related_name='cd_related_documents',
        blank=True)

    # Schedule
    status_std_planned_date = models.DateField(
        verbose_name=u"Status STD Planned Date",
        null=True, blank=True)
    status_std_forecast_date = models.DateField(
        verbose_name=u"Status STD Forecast Date",
        null=True, blank=True)
    status_std_actual_date = models.DateField(
        verbose_name=u"Status STD Actual Date",
        null=True, blank=True)
    status_idc_planned_date = models.DateField(
        verbose_name=u"Status IDC Planned Date",
        null=True, blank=True)
    status_idc_forecast_date = models.DateField(
        verbose_name=u"Status IDC Forecast Date",
        null=True, blank=True)
    status_idc_actual_date = models.DateField(
        verbose_name=u"Status IDC Actual Date",
        null=True, blank=True)
    status_ifr_planned_date = models.DateField(
        verbose_name=u"Status IFR Planned Date",
        null=True, blank=True)
    status_ifr_forecast_date = models.DateField(
        verbose_name=u"Status IFR Forecast Date",
        null=True, blank=True)
    status_ifr_actual_date = models.DateField(
        verbose_name=u"Status IFR Actual Date",
        null=True, blank=True)
    status_ifa_planned_date = models.DateField(
        verbose_name=u"Status IFA Planned Date",
        null=True, blank=True)
    status_ifa_forecast_date = models.DateField(
        verbose_name=u"Status IFA Forecast Date",
        null=True, blank=True)
    status_ifa_actual_date = models.DateField(
        verbose_name=u"Status IFA Actual Date",
        null=True, blank=True)
    status_ifd_planned_date = models.DateField(
        verbose_name=u"Status IFD Planned Date",
        null=True, blank=True)
    status_ifd_forecast_date = models.DateField(
        verbose_name=u"Status IFD Forecast Date",
        null=True, blank=True)
    status_ifd_actual_date = models.DateField(
        verbose_name=u"Status IFD Actual Date",
        null=True, blank=True)
    status_ifc_planned_date = models.DateField(
        verbose_name=u"Status IFC Planned Date",
        null=True, blank=True)
    status_ifc_forecast_date = models.DateField(
        verbose_name=u"Status IFC Forecast Date",
        null=True, blank=True)
    status_ifc_actual_date = models.DateField(
        verbose_name=u"Status IFC Actual Date",
        null=True, blank=True)
    status_ifi_planned_date = models.DateField(
        verbose_name=u"Status IFI Planned Date",
        null=True, blank=True)
    status_ifi_forecast_date = models.DateField(
        verbose_name=u"Status IFI Forecast Date",
        null=True, blank=True)
    status_ifi_actual_date = models.DateField(
        verbose_name=u"Status IFI Actual Date",
        null=True, blank=True)
    status_asb_planned_date = models.DateField(
        verbose_name=u"Status ASB Planned Date",
        null=True, blank=True)
    status_asb_forecast_date = models.DateField(
        verbose_name=u"Status ASB Forecast Date",
        null=True, blank=True)
    status_asb_actual_date = models.DateField(
        verbose_name=u"Status ASB Actual Date",
        null=True, blank=True)

    class PhaseConfig:
        filter_fields = (
            'docclass', 'status', 'unit', 'discipline',
            'document_type', 'under_review', 'overdue', 'leader', 'approver'
        )
        searchable_fields = ('document_key', 'title',)
        indexable_fields = ['is_existing']
        column_fields = (
            ('Document Number', 'document_key'),
            ('Title', 'title'),
            ('Rev.', 'current_revision'),
            ('Status', 'status'),
            ('Class', 'docclass'),
            ('Unit', 'unit'),
            ('Discipline', 'discipline'),
            ('Document type', 'document_type'),
            ('Review start date', 'review_start_date'),
            ('Review due date', 'review_due_date'),
            ('Under review', 'under_review'),
            ('Overdue', 'overdue'),
            ('Leader', 'leader'),
            ('Approver', 'approver'),
            ('Final revision', 'final_revision'),
        )
        transmittal_columns = {
            'Document Number': 'document_key',
            'Title': 'title',
            'Contract Number': 'contract_number',
            'Originator': 'originator',
            'Unit': 'unit',
            'Discipline': 'discipline',
            'Document Type': 'document_type',
            'Sequential Number': 'sequential_number',
            'Class': 'docclass',
            'Revision': 'revision',
            'Status': 'status',
            'Received Date': 'received_date',
            'Created': 'created_on',
        }
        export_fields = OrderedDict((
            ('Document Number', 'document_key'),
            ('Title', 'title'),
            ('Revision', 'revision_name'),
            ('Revision date', 'revision_date'),
            ('Status', 'status'),
            ('Doc category', 'category'),
            ('Class', 'docclass'),
            ('Contract Number', 'contract_number'),
            ('Originator', 'originator'),
            ('Unit', 'unit'),
            ('Discipline', 'discipline'),
            ('Sequential Number', 'sequential_number'),
            ('System', 'system'),
            ('WBS', 'wbs'),
            ('Weight', 'weight'),
            ('Is final revision', 'final_revision'),
            ('Received date', 'received_date'),
            ('Created on', 'created_on'),
            ('Review start date', 'review_start_date'),
            ('Review due date', 'review_due_date'),
            ('Leader', 'leader'),
            ('Approver', 'approver'),
            ('Return code', 'return_code'),
        ))
        custom_filters = {
            'show_cld_spd': {
                'field': forms.BooleanField,
                'label': _('Show CLD/SPD docs'),
                'filters': {
                    True: None,
                    False: F('term', is_existing=True),
                    None: F('term', is_existing=True)
                }
            }
        }

    class Meta:
        ordering = ('document_key',)
        unique_together = (
            (
                "contract_number", "originator", "unit", "discipline",
                "document_type", "sequential_number",
            ),
        )

    def natural_key(self):
        return self.document_key

    def generate_document_key(self):
        return slugify(
            u"{contract_number}-{originator}-{unit}-{discipline}-"
            u"{document_type}-{sequential_number}"
            .format(
                contract_number=self.contract_number,
                originator=self.originator,
                unit=self.unit,
                discipline=self.discipline,
                document_type=self.document_type,
                sequential_number=self.sequential_number
            )).upper()

    def get_all_revisions(self):
        """Return all revisions data of this document."""
        revisions = super(ContractorDeliverable, self) \
            .get_all_revisions() \
            .select_related(
                'document',
                'document__category__organisation',
                'leader',
                'approver') \
            .prefetch_related('reviewers')

        return revisions

    @property
    def status(self):
        return self.latest_revision.status

    @property
    def is_existing(self):
        return self.status not in ('CLD', 'SPD')

    @property
    def final_revision(self):
        return self.latest_revision.final_revision

    @property
    def review_start_date(self):
        return self.latest_revision.review_start_date

    @property
    def review_due_date(self):
        return self.latest_revision.review_due_date

    @property
    def under_review(self):
        return self.latest_revision.is_under_review()

    @property
    def overdue(self):
        return self.latest_revision.is_overdue()

    @property
    def leader(self):
        return self.latest_revision.leader

    @property
    def approver(self):
        return self.latest_revision.approver

    @property
    def docclass(self):
        return self.latest_revision.docclass


class ContractorDeliverableRevision(ReviewMixin, MetadataRevision):
    # Revision
    status = ConfigurableChoiceField(
        verbose_name=u"Status",
        default="STD",
        max_length=3,
        list_index='STATUSES',
        null=True, blank=True)
    final_revision = models.NullBooleanField(
        _('Is final revision?'),
        choices=BOOLEANS,
        null=True,
        blank=True)


class Correspondence(Metadata):
    latest_revision = models.ForeignKey(
        'CorrespondenceRevision',
        verbose_name=_('Latest revision'))

    # General information
    subject = models.TextField(_('Subject'))
    correspondence_date = models.DateField(_('Correspondence date'))
    received_sent_date = models.DateField(_('Received / sent date'))
    contract_number = ConfigurableChoiceField(
        _('Contract Number'),
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
    document_type = ConfigurableChoiceField(
        _('Document Type'),
        default="PID",
        max_length=3,
        list_index='DOCUMENT_TYPES')
    sequential_number = models.CharField(
        verbose_name=u"sequential Number",
        help_text=_('Type in a four digit number'),
        default=u"0001",
        max_length=4,
        validators=[StringNumberValidator(4)])
    author = ConfigurableChoiceField(
        _('Author'),
        null=True,
        blank=True,
        max_length=250,
        list_index='AUTHORS')
    addresses = ConfigurableChoiceField(
        _('Addresses'),
        null=True,
        blank=True,
        list_index='ADDRESSES')
    response_required = models.NullBooleanField(
        _('Response required'),
        null=True,
        blank=True)
    due_date = models.DateField(
        _('Due date'),
        null=True,
        blank=True)
    external_reference = models.TextField(
        _('External reference'),
        null=True,
        blank=True)

    # Related documents
    related_documents = models.ManyToManyField(
        'documents.Document',
        related_name='correspondence_related_set',
        blank=True)

    class Meta:
        ordering = ('id',)
        unique_together = (
            (
                "contract_number", "originator", "recipient",
                "document_type", "sequential_number",
            ),
        )

    class PhaseConfig:
        filter_fields = (
            'originator', 'recipient', 'status', 'overdue', 'leader')
        column_fields = (
            ('Reference', 'document_key'),
            ('Subject', 'subject'),
            ('Rec./Sent date', 'received_sent_date'),
            ('Resp. required', 'response_required'),
            ('Due date', 'due_date'),
            ('Status', 'status'),
            ('Under review', 'status'),
            ('Overdue', 'overdue'),
            ('Leader', 'leader'),
            ('Originator', 'originator'),
            ('Recipient', 'recipient'),
            ('Document type', 'document_type'),
        )
        searchable_fields = (
            'document_key',
            'subject',
            'status',
            'leader',
            'originator',
            'recipient',
            'document_type',
        )

    def generate_document_key(self):
        return slugify(
            u"{contract_number}-{originator}-{recipient}-"
            u"{document_type}-{sequential_number}"
            .format(
                contract_number=self.contract_number,
                originator=self.originator,
                recipient=self.recipient,
                document_type=self.document_type,
                sequential_number=self.sequential_number
            )).upper()

    def natural_key(self):
        return (self.document_key,)

    @property
    def status(self):
        return self.latest_revision.status

    @property
    def overdue(self):
        return self.latest_revision.overdue

    @property
    def leader(self):
        return self.latest_revision.leader

    @property
    def title(self):
        return self.subject

    def get_initial_empty(self):
        empty_fields = ('final_revision',)
        return super(ContractorDeliverableRevision, self).get_initial_empty() + empty_fields


class CorrespondenceRevision(MetadataRevision):
    status = ConfigurableChoiceField(
        _('Status'),
        max_length=20,
        list_index='STATUS_COR_MOM')
    under_review = models.NullBooleanField(
        _('Under Review'),
        choices=BOOLEANS,
        null=True, blank=True)
    overdue = models.NullBooleanField(
        _('Overdue'),
        choices=BOOLEANS,
        null=True, blank=True)
    leader = models.ForeignKey(
        User,
        verbose_name=_('Leader'),
        related_name='leading_correspondance',
        null=True, blank=True)


class MinutesOfMeeting(Metadata):
    latest_revision = models.ForeignKey(
        'MinutesOfMeetingRevision',
        verbose_name=_('Latest revision'))

    # General information
    subject = models.TextField(_('Subject'))
    meeting_date = models.DateField(_('Meeting date'))
    received_sent_date = models.DateField(_('Received / sent date'))
    contract_number = ConfigurableChoiceField(
        _('Contract Number'),
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
    document_type = ConfigurableChoiceField(
        _('Document Type'),
        default="PID",
        max_length=3,
        list_index='DOCUMENT_TYPES')
    sequential_number = models.CharField(
        verbose_name=u"sequential Number",
        help_text=_('Type in a four digit number'),
        default=u"0001",
        max_length=4,
        validators=[StringNumberValidator(4)])
    prepared_by = ConfigurableChoiceField(
        _('Prepared by'),
        null=True,
        blank=True,
        max_length=250,
        list_index='AUTHORS')
    signed = models.NullBooleanField(
        _('Signed'),
        null=True, blank=True,
        choices=BOOLEANS)

    # Response reference
    # TODO Check the queryset
    response_reference = models.ManyToManyField(
        'Correspondence',
        related_name='mom_correspondence_related_set',
        blank=True)

    class Meta:
        ordering = ('document_key',)
        unique_together = (
            (
                "contract_number", "originator", "recipient",
                "document_type", "sequential_number",
            ),
        )

    class PhaseConfig:
        filter_fields = (
            'originator', 'recipient', 'status', 'signed', 'prepared_by',
        )
        column_fields = (
            ('Reference', 'document_key'),
            ('Subject', 'subject'),
            ('Meeting date', 'meeting_date'),
            ('Rec./sent date', 'received_sent_date'),
            ('Originator', 'originator'),
            ('Recipient', 'recipient'),
            ('Document type', 'document_type'),
            ('Prepared by', 'prepared_by'),
            ('Signed', 'signed'),
            ('Status', 'status'),
        )
        searchable_fields = (
            'document_key',
            'subject',
            'originator',
            'recipient',
            'document_type',
            'prepared_by',
            'status',
        )

    def generate_document_key(self):
        return slugify(
            u"{contract_number}-{originator}-{recipient}"
            u"{document_type}-{sequential_number}"
            .format(
                contract_number=self.contract_number,
                originator=self.originator,
                recipient=self.recipient,
                document_type=self.document_type,
                sequential_number=self.sequential_number
            )).upper()

    def natural_key(self):
        return (self.document_key,)

    @property
    def status(self):
        return self.latest_revision.status

    @property
    def title(self):
        return self.subject


class MinutesOfMeetingRevision(MetadataRevision):
    status = ConfigurableChoiceField(
        _('Status'),
        max_length=20,
        list_index='STATUS_COR_MOM')


# Those two classes are dummy document classes, used for demos and tests
class DemoMetadata(Metadata):
    latest_revision = models.ForeignKey(
        'DemoMetadataRevision',
        verbose_name=_('Latest revision'),
        null=True)
    title = models.CharField(
        _('Title'),
        max_length=250)
    related_documents = models.ManyToManyField(
        'documents.Document',
        related_name='demometadata_related_set',
        blank=True)

    class Meta:
        ordering = ('document_key',)

    class PhaseConfig:
        filter_fields = ('status',)
        searchable_fields = (
            'title', 'document_key', 'title',
        )
        column_fields = (
            ('Document Number', 'document_key'),
            ('Title', 'title'),
            ('Status', 'status'),
        )
        transmittal_columns = {
            'Document Number': 'document_key',
            'Title': 'title',
            'Contract Number': 'contract_number',
            'Originator': 'originator',
            'Unit': 'unit',
            'Discipline': 'discipline',
            'Document Type': 'document_type',
            'Sequential Number': 'sequential_number',
            'Class': 'docclass',
            'Revision': 'revision',
            'Status': 'status',
            'Received Date': 'revision_date',
            'Created': 'created_on',
        }

    def natural_key(self):
        return (self.document_key,)

    def generate_document_key(self):
        return slugify(self.title)

    @property
    def status(self):
        return self.latest_revision.status


class DemoMetadataRevision(ReviewMixin, MetadataRevision):
    STATUSES = (
        ('STD', 'Started'),
        ('IDC', 'Inter Discipline Check'),
        ('IFR', 'Issued For Review'),
        ('IFA', 'Issued For Approval'),
        ('IFD', 'Issued For Design'),
        ('IFC', 'Issued For Construction'),
        ('FIN', 'Final'),
        ('IFI', 'Issued For Information'),
        ('ASB', 'As Built'),
        ('CLD', 'Cancelled'),
        ('SPD', 'Superseded'),
        ('ANA', 'Analysis'),
        ('BAS', 'Design Basis'),
    )
    status = models.CharField(
        verbose_name=_('Status'),
        default="STD",
        max_length=3,
        choices=STATUSES,
        null=True, blank=True)
