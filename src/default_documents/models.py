# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid
from collections import OrderedDict

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django import forms

from elasticsearch_dsl import F

from metadata.fields import ConfigurableChoiceField
from accounts.models import User
from reviews.models import ReviewMixin
from transmittals.models import TransmittableMixin
from documents.models import Metadata, MetadataRevision
from documents.constants import BOOLEANS
from documents.templatetags.documents import MenuItem
from schedules.models import ScheduleMixin
from .validators import StringNumberValidator


class ContractorDeliverable(ScheduleMixin, Metadata):
    latest_revision = models.ForeignKey(
        'ContractorDeliverableRevision',
        null=True,
        verbose_name=_('Latest revision'))

    # General information
    title = models.TextField(
        verbose_name=u"Title")
    # Let's keep this field for a while
    contract_number_old = ConfigurableChoiceField(
        verbose_name=u"Contract Number",
        max_length=15,
        list_index='CONTRACT_NBS', null=True, blank=True)
    contract_number = models.CharField(
        verbose_name='Contract Number',
        max_length=50)
    originator = models.ForeignKey(
        'accounts.Entity',
        verbose_name=_('Originator'))
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
        indexable_fields = ['is_existing', 'can_be_transmitted']
        es_field_types = {
            'overdue': 'boolean',
        }
        column_fields = (
            ('', 'under_preparation_by'),
            ('Document Number', 'document_number'),
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
            ('Document number', 'document_number'),
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
            ('Document type', 'document_type'),
            ('Sequential number', 'sequential_number'),
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
            ('Outgoing transmittal', 'transmittal'),
            ('Sent date', 'transmittal_sent_date'),
            ('Purpose of issue', 'purpose_of_issue'),
            ('External due date', 'external_review_due_date'),
            ('Return code', 'return_code'),
            ('STD Planned', 'status_std_planned_date'),
            ('IDC Planned', 'status_idc_planned_date'),
            ('IFR Planned', 'status_ifr_planned_date'),
            ('IFA Planned', 'status_ifa_planned_date'),
            ('IFD Planned', 'status_ifd_planned_date'),
            ('IFC Planned', 'status_ifc_planned_date'),
            ('IFI Planned', 'status_ifi_planned_date'),
            ('ASB Planned', 'status_asb_planned_date'),
            ('STD Forecast', 'status_std_forecast_date'),
            ('IDC Forecast', 'status_idc_forecast_date'),
            ('IFR Forecast', 'status_ifr_forecast_date'),
            ('IFA Forecast', 'status_ifa_forecast_date'),
            ('IFD Forecast', 'status_ifd_forecast_date'),
            ('IFC Forecast', 'status_ifc_forecast_date'),
            ('IFI Forecast', 'status_ifi_forecast_date'),
            ('ASB Forecast', 'status_asb_forecast_date'),
            ('STD Actual', 'status_std_actual_date'),
            ('IFR Actual', 'status_ifr_actual_date'),
            ('IDC Actual', 'status_idc_actual_date'),
            ('IFA Actual', 'status_ifa_actual_date'),
            ('IFD Actual', 'status_ifd_actual_date'),
            ('IFC Actual', 'status_ifc_actual_date'),
            ('IFI Actual', 'status_ifi_actual_date'),
            ('ASB Actual', 'status_asb_actual_date'),
        ))
        custom_filters = OrderedDict((
            ('show_cld_spd', {
                'field': forms.BooleanField,
                'label': _('Show CLD/SPD docs'),
                'filters': {
                    True: None,
                    False: F('term', is_existing=True),
                    None: F('term', is_existing=True)
                }
            }),
            ('outgoing_trs', {
                'field': forms.BooleanField,
                'label': _('Ready for outgoing TRS'),
                'filters': {
                    True: F('term', can_be_transmitted=True),
                    False: None,
                    None: None,
                }
            }))
        )

    class Meta:
        ordering = ('document_number',)
        app_label = 'default_documents'
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
                originator=self.originator.trigram,
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
                'metadata',
                'metadata__document',
                'metadata__document__category__organisation',
                'leader',
                'approver',
                'approver',
                'transmittal__document') \
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

    @classmethod
    def get_batch_actions(cls, category, user):
        actions = super(ContractorDeliverable, cls).get_batch_actions(
            category, user)

        if user.has_perm('documents.can_control_document') and user.has_perm('reviews.can_add_review'):
            actions['start_review'] = MenuItem(
                'start-review',
                _('Start review'),
                reverse('batch_start_reviews', args=[
                    category.organisation.slug,
                    category.slug]),
                ajax=True,
                modal='batch-review-modal',
                progression_modal=True,
                icon='eye-open',
            )
            actions['cancel_review'] = MenuItem(
                'cancel-review',
                _('Cancel review'),
                reverse('batch_cancel_reviews', args=[
                    category.organisation.slug,
                    category.slug]),
                ajax=True,
                modal='cancel-review-modal',
                progression_modal=True,
                icon='eye-close',
            )

        if user.has_perm('transmittals.add_outgoingtransmittal'):
            actions['prepare_transmittal'] = MenuItem(
                'prepare-transmittal',
                _('Prepare outgoing transmittal'),
                reverse('transmittal_prepare', args=[
                    category.organisation.slug,
                    category.slug]),
                ajax=False,
                progression_modal=False,
                icon='hand-up'
            )
            actions['create_transmittal'] = MenuItem(
                'create-transmittal',
                'Create transmittal',
                reverse('transmittal_create', args=[
                    category.organisation.slug,
                    category.slug]),
                ajax=True,
                modal='create-transmittal-modal',
                progression_modal=True,
                icon='transfer',
            )
        return actions

    @classmethod
    def get_batch_actions_modals(cls):
        templates = super(ContractorDeliverable, cls).get_batch_actions_modals()
        return templates + [
            'reviews/document_list_cancel_review_modal.html',
            'reviews/document_list_batch_review_modal.html',
            'transmittals/document_list_create_transmittal_modal.html'
        ]


class ContractorDeliverableRevision(TransmittableMixin, MetadataRevision):
    # Revision
    metadata = models.ForeignKey('ContractorDeliverable')
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

    class Meta:
        app_label = 'default_documents'


class Correspondence(Metadata):
    latest_revision = models.ForeignKey(
        'CorrespondenceRevision',
        null=True,
        verbose_name=_('Latest revision'))

    # General information
    subject = models.TextField(_('Subject'))
    correspondence_date = models.DateField(_('Correspondence date'))
    received_sent_date = models.DateField(_('Received / sent date'))
    contract_number_old = ConfigurableChoiceField(
        _('Contract Number'),
        max_length=8,
        list_index='CONTRACT_NBS', null=True, blank=True)
    contract_number = models.CharField(
        verbose_name='Contract Number',
        max_length=50)
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
        app_label = 'default_documents'
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
            ('Reference', 'document_number'),
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
    metadata = models.ForeignKey('Correspondence')
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

    class Meta:
        app_label = 'default_documents'


class MinutesOfMeeting(Metadata):
    latest_revision = models.ForeignKey(
        'MinutesOfMeetingRevision',
        null=True,
        verbose_name=_('Latest revision'))

    # General information
    subject = models.TextField(_('Subject'))
    meeting_date = models.DateField(_('Meeting date'))
    received_sent_date = models.DateField(_('Received / sent date'))
    # We keep it for a while
    contract_number_old = ConfigurableChoiceField(
        _('Contract Number'),
        max_length=8,
        list_index='CONTRACT_NBS', blank=True, null=True)
    contract_number = models.CharField(
        verbose_name='Contract Number',
        max_length=50
    )
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
        ordering = ('document_number',)
        app_label = 'default_documents'
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
            ('Reference', 'document_number'),
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
    metadata = models.ForeignKey('MinutesOfMeeting')
    status = ConfigurableChoiceField(
        _('Status'),
        max_length=20,
        list_index='STATUS_COR_MOM')

    class Meta:
        app_label = 'default_documents'


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
        ordering = ('document_number',)
        app_label = 'default_documents'

    class PhaseConfig:
        filter_fields = ('status',)
        column_fields = (
            ('Document Number', 'document_number'),
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
    metadata = models.ForeignKey('DemoMetadata')
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

    class Meta:
        app_label = 'default_documents'


class GtgMetadata(Metadata):
    latest_revision = models.ForeignKey(
        'GtgMetadataRevision',
        null=True,
        verbose_name=_('Latest revision'))
    title = models.TextField(_('title'))
    originator = models.ForeignKey(
        'accounts.Entity',
        verbose_name=_('Originator'),
        limit_choices_to={'type': 'originator'})
    unit = ConfigurableChoiceField(
        verbose_name=u"Unit",
        default="000",
        max_length=3,
        list_index='GTG_UNITS')
    discipline = ConfigurableChoiceField(
        _('Discipline'),
        max_length=6,
        list_index='GTG_DISCIPLINES',
        blank=True,
        null=True)
    document_type = ConfigurableChoiceField(
        _('Document Type'),
        max_length=3,
        list_index='GTG_DOCUMENT_TYPES')

    # Related docs
    related_documents = models.ManyToManyField(
        'documents.Document',
        related_name='gtg_related_documents',
        blank=True)

    # Schedule
    status_ifr_planned_date = models.DateField(
        _('Status IFR Planned Date'),
        null=True, blank=True)
    status_ifr_forecast_date = models.DateField(
        _('Status IFR Forecast Date'),
        null=True, blank=True)
    status_ifr_actual_date = models.DateField(
        _('Status IFR Actual Date'),
        null=True, blank=True)

    status_ifa_planned_date = models.DateField(
        _('Status IFA Planned Date'),
        null=True, blank=True)
    status_ifa_forecast_date = models.DateField(
        _('Status IFA Forecast Date'),
        null=True, blank=True)
    status_ifa_actual_date = models.DateField(
        _('Status IFA Actual Date'),
        null=True, blank=True)

    status_ifi_planned_date = models.DateField(
        _('Status IFI Planned Date'),
        null=True, blank=True)
    status_ifi_forecast_date = models.DateField(
        _('Status IFI Forecast Date'),
        null=True, blank=True)
    status_ifi_actual_date = models.DateField(
        _('Status IFI Actual Date'),
        null=True, blank=True)

    status_ife_planned_date = models.DateField(
        _('Status IFE Planned Date'),
        null=True, blank=True)
    status_ife_forecast_date = models.DateField(
        _('Status IFE Forecast Date'),
        null=True, blank=True)
    status_ife_actual_date = models.DateField(
        _('Status IFE Actual Date'),
        null=True, blank=True)

    status_ifp_planned_date = models.DateField(
        _('Status IFP Planned Date'),
        null=True, blank=True)
    status_ifp_forecast_date = models.DateField(
        _('Status IFP Forecast Date'),
        null=True, blank=True)
    status_ifp_actual_date = models.DateField(
        _('Status IFP Actual Date'),
        null=True, blank=True)

    status_fin_planned_date = models.DateField(
        _('Status FIN Planned Date'),
        null=True, blank=True)
    status_fin_forecast_date = models.DateField(
        _('Status FIN Forecast Date'),
        null=True, blank=True)
    status_fin_actual_date = models.DateField(
        _('Status FIN Actual Date'),
        null=True, blank=True)

    status_asb_planned_date = models.DateField(
        _('Status ASB Planned Date'),
        null=True, blank=True)
    status_asb_forecast_date = models.DateField(
        _('Status ASB Forecast Date'),
        null=True, blank=True)
    status_asb_actual_date = models.DateField(
        _('Status ASB Actual Date'),
        null=True, blank=True)

    class Meta:
        verbose_name = _('Gtg deliverable')
        verbose_name_plural = _('Gtg deliverables')
        ordering = ('document_number',)

    class PhaseConfig:
        filter_fields = [
            'originator',
            'discipline',
            'document_type',
            'status',
            'unit',
            'leader',
            'approver',
            'under_review',
            'overdue']
        filter_fields_order_ = [
            'search_terms',
            'originator',
            'discipline',
            'document_type',
            'status',
            'unit',
            'leader',
            'approver',
            'under_review',
            'overdue']

        column_fields = (
            ('Document Number', 'document_number'),
            ('Title', 'title'),
            ('Status', 'status'),
            ('Rev.', 'current_revision'),
            ('Document type', 'document_type'),
            ('Originator', 'originator'),
            ('Review start date', 'review_start_date'),
            ('Review due date', 'review_due_date'),
            ('Under review', 'under_review'),
            ('Leader', 'leader'),
            ('Approver', 'approver'),
        )

    def natural_key(self):
        return self.document_key

    def generate_document_key(self):
        # If document key is not suppplied by user, we generate a uuid
        return '{}'.format(uuid.uuid4())

    @property
    def status(self):
        return self.latest_revision.status

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
    def received_date(self):
        return self.latest_revision.received_date

    @property
    def leader_step_closed(self):
        return self.latest_revision.leader_step_closed

    @property
    def review_end_date(self):
        return self.latest_revision.review_end_date

    @property
    def return_code(self):
        return self.latest_revision.return_code

    @classmethod
    def get_batch_actions(cls, category, user):
        actions = super(GtgMetadata, cls).get_batch_actions(
            category, user)
        actions['start_review'] = MenuItem(
            'start-review',
            _('Start review'),
            reverse('batch_start_reviews', args=[
                category.organisation.slug,
                category.slug]),
            ajax=True,
            modal='batch-review-modal',
            progression_modal=True,
            icon='eye-open',
        )
        actions['cancel_review'] = MenuItem(
            'cancel-review',
            'Cancel review',
            reverse('batch_cancel_reviews', args=[
                category.organisation.slug,
                category.slug]),
            ajax=True,
            modal='cancel-review-modal',
            progression_modal=True,
            icon='eye-close',
        )
        if user.has_perm('transmittals.add_outgoingtransmittal'):
            actions['create_transmittal'] = MenuItem(
                'create-transmittal',
                'Create transmittal',
                reverse('transmittal_create', args=[
                    category.organisation.slug,
                    category.slug]),
                ajax=True,
                modal='create-transmittal-modal',
                progression_modal=True,
                icon='transfer',
            )
        return actions

    @classmethod
    def get_batch_actions_modals(cls):
        templates = super(GtgMetadata, cls).get_batch_actions_modals()
        return templates + [
            'reviews/document_list_cancel_review_modal.html',
            'reviews/document_list_batch_review_modal.html',
            'transmittals/document_list_create_transmittal_modal.html'
        ]


class GtgMetadataRevision(TransmittableMixin, MetadataRevision):
    metadata = models.ForeignKey('GtgMetadata')
    status = ConfigurableChoiceField(
        _('Status'),
        max_length=3,
        list_index='GTG_STATUSES',
        null=True, blank=True)
    final_revision = models.NullBooleanField(
        _('Is final revision?'),
        choices=BOOLEANS,
        null=True,
        blank=True)

    def get_first_revision_number(self):
        """See `MetadataRevision.get_first_revision_number`"""
        return 1
