from django.db import models
from django.utils.translation import ugettext_lazy as _

from .fields import ConfigurableChoiceField


class ValuesList(models.Model):
    """Administrable key / value list to use in Choices fields."""
    index = models.CharField(
        _('Index'),
        max_length=50,
        db_index=True)
    name = models.CharField(
        _('Name'),
        max_length=255)

    class Meta:
        verbose_name = _('Values list')
        verbose_name_plural = _('Values lists')

    def __unicode__(self):
        return self.name


class ListEntry(models.Model):
    """Single entry in a values list."""
    values_list = models.ForeignKey(
        ValuesList,
        verbose_name=_('List'),
        related_name='values')
    order = models.PositiveIntegerField(
        _('Order'),
        default=0
    )
    index = models.CharField(
        _('Index'),
        max_length=50)
    value = models.CharField(
        _('Value'),
        max_length=255,
        blank=True)

    class Meta:
        verbose_name = _('List entry')
        verbose_name_plural = _('List entries')
        ordering = ('order', 'index')

    def __unicode__(self):
        return '%s - %s' % (self.index, self.value)


class ContractorDeliverable(models.Model):

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
#    document_type = models.CharField(
#        verbose_name=u"Document Type",
#        default="PID",
#        max_length=3,
#        choices=DOCUMENT_TYPES)
#    sequencial_number = models.CharField(
#        verbose_name=u"Sequencial Number",
#        default=u"0001",
#        max_length=4,
#        choices=SEQUENCIAL_NUMBERS)
#    project_phase = models.CharField(
#        verbose_name=u"Project Phase",
#        default=u"FEED",
#        max_length=4,
#        choices=ENGINEERING_PHASES)
#    klass = models.IntegerField(
#        verbose_name=u"Class",
#        default=1,
#        choices=CLASSES)
#    system = models.IntegerField(
#        verbose_name=u"System",
#        choices=SYSTEMS,
#        null=True, blank=True)
#    wbs = models.CharField(
#        verbose_name=u"WBS",
#        max_length=20,
#        choices=WBS,
#        null=True, blank=True)
#    weight = models.IntegerField(
#        verbose_name=u"Weight",
#        null=True, blank=True)
#
#    # Revision
#    current_revision = models.ForeignKey(
#        'ContractorDeliverableRevision'
#    )
#
#    related_documents = models.ManyToManyField(
#        'Document',
#        null=True, blank=True)
#    schedule = models.DateField()
#
#    created_on = models.DateField(
#        auto_now_add=True,
#        verbose_name=u"Created on")
#    updated_on = models.DateTimeField(
#        auto_now=True,
#        verbose_name=u"Updated on")

    class Meta:
        verbose_name = _('Contractor deliverable')
        verbose_name_plural = _('Contractor deliverables')
        ordering = ('document_number',)
        #unique_together = (
        #    (
        #        "contract_number", "originator", "unit", "discipline",
        #        "document_type", "sequencial_number",
        #    ),
        #)


#class ContractorDeliverableRevision(models.Model):
#    # Revision
#    revision = models.CharField(
#        verbose_name=u"Revision",
#        default=u"00",
#        max_length=2,
#        choices=REVISIONS)
#    revision_date = models.DateField(
#        verbose_name=u"Revision Date")
#    created_on = models.DateField(
#        auto_now_add=True,
#        verbose_name=u"Created on")
#    final_revision = models.BooleanField(
#    )
#    native_file = models.FileField(
#        verbose_name=u"Native File",
#        upload_to=upload_to_path,
#        storage=private_storage,
#        null=True, blank=True)
#    pdf_file = models.FileField(
#        verbose_name=u"PDF File",
#        upload_to=upload_to_path,
#        storage=private_storage,
#        null=True, blank=True)
#    review_start_date = models.DateField()
#    review_due_date = models.DateField()
#    review_countdown = models.IntegerField()
#    under_review = models.BooleanField()
#    overdue = models.BooleanField()
#    reviewers = models.ManyToManyField()
#    leader = models.ForeignKeyField()
#    leader_comments = models.FileField()
#    approver = models.ForeignKeyField()
#    approver_comments = models.FileField()
#    under_gtg_review = models.BooleanField()
#    under_contractor_review = models.NullBooleanField(
#        verbose_name=u"Under Contractor Review",
#        choices=BOOLEANS,
#        null=True, blank=True)
#
#    document = models.ForeignKey(ContractorDeliverable)
#
#    class Meta:
#        ordering = ('-revision',)
#        get_latest_by = 'revision'
