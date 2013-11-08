#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


from metadata.fields import ConfigurableChoiceField
from accounts.models import User
from .fileutils import upload_to_path, private_storage
from .constants import (
    BOOLEANS, SEQUENTIAL_NUMBERS, CLASSES, REVISIONS
)


class Document(models.Model):
    document_key = models.CharField(
        _('Document key'),
        max_length=250)
    favorited_by = models.ManyToManyField(
        User,
        through='favorites.Favorite',
        null=True, blank=True)

    metadata_type = models.ForeignKey(ContentType)
    metadata_id = models.PositiveIntegerField()
    metadata = generic.GenericForeignKey('metadata_type', 'metadata_id')

    # Used by favorites
    #title
    #current_revision
    # document_number / natural_key
    # updated_on

    class Meta:
        verbose_name = _('Document')
        verbose_name_plural = _('Documents')

    def save(self, *args, **kwargs):
        # TODO : get document key from metadata object
        super(Document, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ('document_detail', [self.natural_key])


class Metadata(models.Model):
    created_on = models.DateField(
        _('Created on'),
        auto_now_add=True)
    updated_on = models.DateTimeField(
        _('Updated on'),
        auto_now=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.natural_key()

    def natural_key(self):
        raise NotImplementedError()

    def get_column_fields(self):
        raise NotImplementedError()


class MetadataRevision(models.Model):
    document = models.ForeignKey(Document)

    revision = models.CharField(
        verbose_name=u"Revision",
        default=u"00",
        max_length=2,
        choices=REVISIONS)
    revision_date = models.DateField(
        auto_now_add=True,
        verbose_name=u"Revision Date")
    created_on = models.DateField(
        _('Created on'),
        auto_now_add=True)
    updated_on = models.DateTimeField(
        _('Updated on'),
        auto_now=True)

    class Meta:
        abstract = True
        ordering = ('-revision',)
        get_latest_by = 'revision'


class ContractorDeliverable(Metadata):

    # General information
    document_number = models.CharField(
        verbose_name=u"Document Number",
        max_length=30)
    title = models.TextField(
        verbose_name=u"Title")
    contract_number = ConfigurableChoiceField(
        verbose_name=u"Contract Number",
        max_length=8,
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
    sequencial_number = models.CharField(
        verbose_name=u"Sequencial Number",
        default=u"0001",
        max_length=4,
        choices=SEQUENTIAL_NUMBERS)
    project_phase = ConfigurableChoiceField(
        verbose_name=u"Engineering Phase",
        default=u"FEED",
        max_length=4,
        list_index='ENGINEERING_PHASES')
    klass = models.IntegerField(
        verbose_name=u"Class",
        default=1,
        choices=CLASSES)
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

    # Revision
    current_revision = ConfigurableChoiceField(
        verbose_name=u"Revision",
        default=u"00",
        max_length=2,
        list_index='REVISIONS')
    current_revision_date = models.DateField(
        verbose_name=u"Revision Date")

    # Related documents
    related_documents = models.ManyToManyField(
        'Document',
        null=True, blank=True)

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

    class Meta:
        ordering = ('document_number',)
        unique_together = (
            (
                "contract_number", "originator", "unit", "discipline",
                "document_type", "sequencial_number",
            ),
        )

    def natural_key(self):
        return self.document_number

    def save(self, *args, **kwargs):
        """The document number is generated from multiple fields

        if not specified.
        """
        if not self.document_number:
            self.document_number = (
                u"{contract_number}-{originator}-{unit}-{discipline}-"
                u"{document_type}-{sequencial_number}").format(
                    contract_number=self.contract_number,
                    originator=self.originator,
                    unit=self.unit,
                    discipline=self.discipline,
                    document_type=self.document_type,
                    sequencial_number=self.sequencial_number
                )
        super(Document, self).save(*args, **kwargs)

    def display_fields(self):
        """The list of fields to display in a concise way."""
        return [
            (u'Document Number', u'document_number', self.document_number),
            (u'Title', u'title', self.title),
            (u'Rev. Date', u'current_revision_date', self.current_revision_date),
            (u'Rev.', u'current_revision', self.current_revision),
            (u'Status', u'status', self.status),
        ]

    def searchable_fields(self):
        """The list of fields to search into."""
        return [
            u'document_number',
            u'title',
            u'status',
            u'unit',
            u'discipline',
            u'document_type',
            u'klass',
            u'contract_number',
            u'originator',
            u'sequencial_number',
        ]

    def jsonified(self, document2favorite={}):
        """Returns a list of document values ready to be json-encoded.

        The first element of the list is the linkified document number.
        """
        favorited = self.pk in document2favorite.keys()
        fields_infos = dict((field[1], unicode(field[2]))
                            for field in self.display_fields())
        fields_infos.update({
            u'url': self.get_absolute_url(),
            u'number': self.document_number,
            u'pk': self.pk,
            u'favorite_id': document2favorite.get(self.pk, u''),
            u'favorited': favorited,
        })
        return fields_infos

    def latest_revision(self):
        """Returns the latest revision related to this document."""
        return self.documentrevision_set.all().latest()


class ContractorDeliverableRevision(MetadataRevision):
    # Revision
    status = ConfigurableChoiceField(
        verbose_name=u"Status",
        default="STD",
        max_length=3,
        list_index='STATUSES',
        null=True, blank=True)
    final_revision = models.BooleanField(
        _('Is final revision?'),
        default=False)
    native_file = models.FileField(
        verbose_name=u"Native File",
        upload_to=upload_to_path,
        storage=private_storage,
        null=True, blank=True)
    pdf_file = models.FileField(
        verbose_name=u"PDF File",
        upload_to=upload_to_path,
        storage=private_storage,
        null=True, blank=True)

    # Review
    review_start_date = models.DateField(
        _('Review start date'),
        null=True, blank=True
    )
    review_due_date = models.DateField(
        _('Review due date'),
        null=True, blank=True
    )
    # review_countdown = due_date - now
    under_review = models.NullBooleanField(
        verbose_name=u"Under Review",
        choices=BOOLEANS,
        null=True, blank=True)
    under_contractor_review = models.NullBooleanField(
        verbose_name=u"Under Contractor Review",
        choices=BOOLEANS,
        null=True, blank=True)
    overdue = models.NullBooleanField(
        _('Overdue'),
        choices=BOOLEANS,
        null=True, blank=True)
    reviewers = models.ManyToManyField(
        User,
        verbose_name=_('Reviewers'),
        null=True, blank=True)
    leader = models.ForeignKey(
        User,
        verbose_name=_('Leader'),
        related_name='leading_contractor_deliverables',
        null=True, blank=True)
    # TODO
    #leader_comments = models.FileField(
    #    _('Leader comments'),
    #    null=True, blank=True)
    approver = models.ForeignKey(
        User,
        verbose_name=_('Approver'),
        related_name='approving_contractor_deliverables',
        null=True, blank=True)
    # TODO
    #approver_comments = models.FileField(
    #    _('Approver comments'),
    #    null=True, blank=True)
    under_gtg_review = models.NullBooleanField(
        _('Under GTG Review'),
        choices=BOOLEANS,
        null=True, blank=True)


class Transmittals(Metadata):

    # General informations
    reference = models.CharField(
        _('Reference'),
        max_length=30)
    transmittal_date = models.DateField(
        _('Transmittal date'))
    ack_of_receipt_date = models.DateField(
        _('Acknowledgment of receipt date'),
        null=True, blank=True)
    contract_number = ConfigurableChoiceField(
        verbose_name=u"Contract Number",
        max_length=8,
        list_index='CONTRACT_NBS')
    originator = ConfigurableChoiceField(
        _('Originator'),
        default=u"FWF",
        max_length=3,
        list_index='ORIGINATORS')
    recipient = ConfigurableChoiceField(
        _('Recipient'),
        default=u"FWF",
        max_length=3,
        list_index='Recipients')
    document_type = ConfigurableChoiceField(
        _('Document Type'),
        default="PID",
        max_length=3,
        list_index='DOCUMENT_TYPES')
    sequencial_number = models.CharField(
        _('Sequencial Number'),
        default=u"0001",
        max_length=4,
        choices=SEQUENTIAL_NUMBERS)
    project_phase = ConfigurableChoiceField(
        _('Engineering Phase'),
        default=u"FEED",
        max_length=4,
        list_index='ENGINEERING_PHASES')
    frm = models.ForeignKey(
        User,
        verbose_name=_('From'),
        related_name='sent_transmittals',
        null=True, blank=True)
    to = models.ForeignKey(
        User,
        verbose_name=_('To'),
        related_name='received_transmittals',
        null=True, blank=True)

    # Revision
    current_revision = ConfigurableChoiceField(
        verbose_name=u"Revision",
        default=u"00",
        max_length=2,
        list_index='REVISIONS')
    current_revision_date = models.DateField(
        verbose_name=u"Revision Date")

    # Related documents
    related_documents = models.ManyToManyField(
        'Document',
        null=True, blank=True)

    class Meta:
        verbose_name = _('Transmittals document')
        verbose_name_plural = _('Transmittals documents')

    def natural_key(self):
        return self.reference


class TransmittalsRevision(MetadataRevision):
    # Revision
    status = ConfigurableChoiceField(
        verbose_name=u"Status",
        default="STD",
        max_length=3,
        list_index='STATUSES',
        null=True, blank=True)
    native_file = models.FileField(
        verbose_name=u"Native File",
        upload_to=upload_to_path,
        storage=private_storage,
        null=True, blank=True)
    pdf_file = models.FileField(
        verbose_name=u"PDF File",
        upload_to=upload_to_path,
        storage=private_storage,
        null=True, blank=True)
