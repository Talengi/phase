from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify

from metadata.fields import ConfigurableChoiceField
from accounts.models import User
from documents.models import Metadata, MetadataRevision
from documents.fileutils import upload_to_path, private_storage
from documents.constants import (
    BOOLEANS, SEQUENTIAL_NUMBERS, CLASSES
)


class ContractorDeliverable(Metadata):
    latest_revision = models.ForeignKey(
        'ContractorDeliverableRevision',
        verbose_name=_('Latest revision'),
        null=True)

    # General information
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
    sequential_number = models.CharField(
        verbose_name=u"sequential Number",
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

    # Related documents
    related_documents = models.ManyToManyField(
        'documents.Document',
        related_name='contractordeliverable_related_set',
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

    class PhaseConfig:
        # TODO Create metaclass to validate those fields
        filter_fields = (
            'status', 'discipline', 'document_type',
            'unit', 'klass', 'contract_number', 'originator',
            'contractor_document_number', 'engineering_phase', 'feed_update',
            'system', 'wbs', 'under_ca_review', 'under_contractor_review',
            'leader', 'approver',
        )
        searchable_fields = (
            'document_key', 'title', 'unit', 'discipline',
            'document_type', 'klass', 'contract_number', 'originator',
            'sequential_number',
        )
        column_fields = (
            ('Document Number', 'document_key', 'document_key'),
            ('Title', 'title', 'title'),
            ('Rev.', 'current_revision', 'latest_revision__revision'),
            ('Rev. Date', 'current_revision_date', 'latest_revision__created_on'),
            ('Status', 'status', 'latest_revision__status'),
        )

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
            ))

    @property
    def current_revision(self):
        return self.latest_revision.revision

    @property
    def current_revision_date(self):
        return self.latest_revision.created_on

    @property
    def status(self):
        return self.latest_revision.status

    def get_all_revisions(self):
        """Return all revisions data of this document."""
        Revision = self.get_revision_class()
        revisions = Revision.objects \
            .filter(document=self.document) \
            .select_related(
                'document',
                'document__category__organisation',
                'leader',
                'approver',
            )
        return revisions


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
    sequential_number = models.CharField(
        _('Sequential Number'),
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
        'documents.Document',
        related_name='transmittals_related_set',
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
