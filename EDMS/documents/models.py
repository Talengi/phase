#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models

from constants import (STATUSES, REVISIONS, CONTRACT_NBS, ORIGINATORS,
                       UNITS, DISCIPLINES, DOCUMENT_TYPES, SEQUENCIAL_NUMBERS,
                       SYSTEMS, ENGINEERING_PHASES, CLASSES,
                       UNDER_CONTRACTOR_REVIEW, UNDER_CA_REVIEW, WBS)


class Document(models.Model):
    title = models.TextField(
        verbose_name=u"Title")
    status = models.CharField(
        verbose_name=u"Status",
        default="IFD",
        max_length=3,
        choices=STATUSES)
    revision = models.CharField(
        verbose_name=u"Revision",
        default=u"00",
        max_length=2,
        choices=REVISIONS)
    revision_date = models.DateField(
        verbose_name=u"Revision Date")
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
    feed_update = models.BooleanField(
        verbose_name=u"FEED Update")
    leader = models.CharField(
        verbose_name=u"Leader",
        max_length=50)
    approver = models.CharField(
        verbose_name=u"Approver",
        max_length=50)
    klass = models.IntegerField(
        verbose_name=u"Class",
        default=1,
        choices=CLASSES)
    under_contractor_review = models.NullBooleanField(
        verbose_name=u"Under Contractor Review",
        choices=UNDER_CONTRACTOR_REVIEW)
    under_ca_review = models.NullBooleanField(
        verbose_name=u"Under CA Review",
        default=False,
        choices=UNDER_CA_REVIEW)
    wbs = models.CharField(
        verbose_name=u"WBS",
        max_length=5,
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

    class Meta:
        # Equivalent to document_number
        ordering = ('contract_number',
                    'originator',
                    'unit',
                    'discipline',
                    'document_type',
                    'sequencial_number',)

    def __unicode__(self):
        return self.document_number

    @property
    def document_number(self):
        """The document number is generated from multiple fields."""
        return (u"{contract_number}-{originator}-{unit}-{discipline}-"
                u"{document_type}-{sequencial_number}").format(
                    contract_number=self.contract_number,
                    originator=self.originator,
                    unit=self.unit,
                    discipline=self.discipline,
                    document_type=self.document_type,
                    sequencial_number=self.sequencial_number
                )

    def display_fields(self):
        """The list of fields to display in a concise way."""
        return [
            #(Name               Column Name         Value)
            (u'Document Number', u'document_number', self.document_number),
            (u'Title',           u'title',           self.title),
            (u'Status',          u'status',          self.status),
            (u'Revision',        u'revision',        self.revision),
            (u'Revision Date',   u'revision_date',   self.revision_date),
            (u'Unit',            u'unit',            self.unit),
            (u'Discipline',      u'discipline',      self.discipline),
            (u'Document Type',   u'document_type',   self.document_type),
            (u'Classe',          u'klass',           self.klass),
        ]

    def searchable_fields(self):
        """The list of fields to search into:

        `display_fields` and `document_number`'s ones.
        """
        return [field[1] for field in self.display_fields()[1:]]\
            + [u'contract_number', u'originator', u'sequencial_number']

    def jsonified(self):
        """Returns a list of document values ready to be json-encoded."""
        return [unicode(field[2]) for field in self.display_fields()]
