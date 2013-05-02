#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings

from documents.constants import (
    STATUSES, REVISIONS, CONTRACT_NBS, ORIGINATORS, UNITS, DISCIPLINES,
    DOCUMENT_TYPES, SEQUENCIAL_NUMBERS, SYSTEMS, ENGINEERING_PHASES,
    CLASSES, BOOLEANS, PEOPLE, WBS
)


class Document(models.Model):
    document_number = models.CharField(
        verbose_name=u"Document Number",
        max_length=30)
    title = models.TextField(
        verbose_name=u"Title")
    status = models.CharField(
        verbose_name=u"Status",
        default="STD",
        max_length=3,
        choices=STATUSES,
        null=True, blank=True)
    created_on = models.DateField(
        auto_now_add=True,
        verbose_name=u"Created on")
    updated_on = models.DateTimeField(
        auto_now=True,
        verbose_name=u"Updated on")
    contract_number = models.CharField(
        verbose_name=u"Contract Number",
        default=u"FAC09001",
        max_length=8,
        choices=CONTRACT_NBS)
    originator = models.CharField(
        verbose_name=u"Originator",
        default=u"FWF",
        max_length=3,
        choices=ORIGINATORS)
    unit = models.CharField(
        verbose_name=u"Unit",
        default="000",
        max_length=3,
        choices=UNITS)
    discipline = models.CharField(
        verbose_name=u"Discipline",
        default="PCS",
        max_length=3,
        choices=DISCIPLINES)
    document_type = models.CharField(
        verbose_name=u"Document Type",
        default="PID",
        max_length=3,
        choices=DOCUMENT_TYPES)
    sequencial_number = models.CharField(
        verbose_name=u"Sequencial Number",
        default=u"0001",
        max_length=4,
        choices=SEQUENCIAL_NUMBERS)
    contractor_document_number = models.CharField(
        verbose_name=u"Contractor Document Number",
        max_length=50,
        null=True, blank=True)
    system = models.IntegerField(
        verbose_name=u"System",
        choices=SYSTEMS,
        null=True, blank=True)
    engeenering_phase = models.CharField(
        verbose_name=u"Engeenering Phase",
        default=u"FEED",
        max_length=4,
        choices=ENGINEERING_PHASES)
    feed_update = models.NullBooleanField(
        choices=BOOLEANS,
        verbose_name=u"FEED Update")
    leader = models.IntegerField(
        verbose_name=u"Leader",
        choices=PEOPLE,
        null=True, blank=True)
    approver = models.IntegerField(
        verbose_name=u"Approver",
        choices=PEOPLE,
        null=True, blank=True)
    klass = models.IntegerField(
        verbose_name=u"Class",
        default=1,
        choices=CLASSES)
    under_contractor_review = models.NullBooleanField(
        verbose_name=u"Under Contractor Review",
        choices=BOOLEANS,
        null=True, blank=True)
    under_ca_review = models.NullBooleanField(
        verbose_name=u"Under CA Review",
        default=False,
        choices=BOOLEANS,
        null=True, blank=True)
    wbs = models.CharField(
        verbose_name=u"WBS",
        max_length=20,
        choices=WBS,
        null=True, blank=True)
    weight = models.IntegerField(
        verbose_name=u"Weight",
        null=True, blank=True)
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
    current_revision = models.CharField(
        verbose_name=u"Revision",
        default=u"00",
        max_length=2,
        choices=REVISIONS)
    current_revision_date = models.DateField(
        verbose_name=u"Revision Date")
    related_documents = models.ManyToManyField(
        'Document',
        null=True, blank=True)
    favorited_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Favorite',
        null=True, blank=True)

    class Meta:
        ordering = ('document_number',)
        unique_together = (
            (
                "contract_number", "originator", "unit", "discipline",
                "document_type", "sequencial_number",
            ),
        )

    def __unicode__(self):
        return self.document_number

    @models.permalink
    def get_absolute_url(self):
        return ('document_detail', [self.document_number])

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
            #(Name               Column Name                Value)
            (u'Document Number', u'document_number',        self.document_number),
            (u'Title',           u'title',                  self.title),
            (u'Status',          u'status',                 self.status),
            (u'Revision',        u'current_revision',       self.current_revision),
            (u'Revision Date',   u'current_revision_date',  self.current_revision_date),
            (u'Unit',            u'unit',                   self.unit),
            (u'Discipline',      u'discipline',             self.discipline),
            (u'Document Type',   u'document_type',          self.document_type),
            (u'Class',           u'klass',                  self.klass),
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

    def jsonified(self, document2favorite={}, favorite_documents_ids=[]):
        """Returns a list of document values ready to be json-encoded.

        The first element of the list is the linkified document number.
        """
        document_link = (
            '<i class="{icon}" data-document-id="{document_id}" '
            'data-favorite-id="{favorite_id}"></i> '
            '<a href="{url}">{number}</a>'
        ).format(
            url=self.get_absolute_url(),
            number=self.document_number,
            document_id=self.pk,
            favorite_id=document2favorite.get(self.pk, ''),
            icon=self.pk in favorite_documents_ids
            and 'icon-star' or 'icon-star-empty',
        )
        return [document_link] \
            + [unicode(field[2]) for field in self.display_fields()[1:]]

    def latest_revision(self):
        """Returns the latest revision related to this document."""
        return self.documentrevision_set.all().latest()


def upload_to_path(instance, filename):
    """Rename document files on upload to match a custom filename

    based on the document number and the revision."""
    return "{number}_{revision}.{extension}".format(
        number=instance.document.document_number,
        revision=instance.revision,
        extension=filename.split('.')[-1]
    )


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    document = models.ForeignKey(Document)
    last_view_date = models.DateTimeField(auto_now_add=True)

    def is_outdated(self):
        """Returns a boolean, True if the document has been updated."""
        return self.last_view_date < self.document.updated_on


class DocumentRevision(models.Model):
    revision = models.CharField(
        verbose_name=u"Revision",
        default=u"00",
        max_length=2,
        choices=REVISIONS)
    revision_date = models.DateField(
        verbose_name=u"Revision Date")
    native_file = models.FileField(
        verbose_name=u"Native File",
        upload_to=upload_to_path,
        null=True, blank=True)
    pdf_file = models.FileField(
        verbose_name=u"PDF File",
        upload_to=upload_to_path,
        null=True, blank=True)
    document = models.ForeignKey(Document)

    class Meta:
        ordering = ('-revision',)
        get_latest_by = 'revision'
