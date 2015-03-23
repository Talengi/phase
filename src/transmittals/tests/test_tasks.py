# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache

from documents.factories import DocumentFactory
from categories.factories import CategoryFactory
from default_documents.factories import (
    ContractorDeliverableFactory, ContractorDeliverableRevisionFactory)
from default_documents.models import ContractorDeliverable
from transmittals.factories import TransmittalFactory, TrsRevisionFactory
from transmittals.tasks import process_transmittal


class ProcessTransmittalTests(TestCase):
    fixtures = ['initial_values_lists']

    def setUp(self):
        # Clear the values list cache
        cache.clear()

        Model = ContentType.objects.get_for_model(ContractorDeliverable)
        self.category = CategoryFactory(category_template__metadata_model=Model)
        self.document = DocumentFactory(
            document_key='FAC10005-CTR-000-EXP-LAY-4891',
            latest_revision=2,
            metadata={
                'title': 'Cause & Effect Chart',
                'contract_number': 'FAC10005',
                'originator': 'CTR',
                'unit': '000',
                'discipline': 'EXP',
                'document_type': 'LAY',
                'sequential_number': '4891',
            },
            revision={
                'revision': 1,
                'docclass': 1,
                'status': 'SPD',
            },
            metadata_factory_class=ContractorDeliverableFactory,
            revision_factory_class=ContractorDeliverableRevisionFactory,
            category=self.category)
        self.metadata = self.document.metadata

        rev2 = ContractorDeliverableRevisionFactory(
            document=self.document,
            revision=2,
            docclass=1,
            status='SPD')
        self.metadata.latest_revision = rev2
        self.metadata.save()

        self.transmittal = TransmittalFactory()
        data = {
            'transmittal': self.transmittal,
            'document': self.document,
            'title': 'Cause & Effect Chart',
            'contract_number': 'FAC10005',
            'originator': 'CTR',
            'unit': '000',
            'discipline': 'EXP',
            'document_type': 'LAY',
            'sequential_number': '4891',
            'docclass': 1,
            'revision': 1,
            'status': 'SPD'}
        TrsRevisionFactory(**data)

        data.update({'revision': 2, 'status': 'IFA'})
        TrsRevisionFactory(**data)

        data.update({'revision': 3, 'docclass': 2})
        TrsRevisionFactory(**data)

        data.update({'revision': 4, 'status': 'FIN'})
        TrsRevisionFactory(**data)

    def test_process_update_revisions(self):
        rev = self.document.metadata.get_revision(2)
        self.assertEqual(rev.status, 'SPD')
        process_transmittal(self.transmittal.pk)

        rev = self.document.metadata.get_revision(2)
        self.assertEqual(rev.status, 'IFA')

    def test_process_create_revisions(self):
        rev = self.document.metadata.get_revision(3)
        self.assertIsNone(rev)

        process_transmittal(self.transmittal.pk)

        rev = self.document.metadata.get_revision(3)
        self.assertIsNotNone(rev)
        self.assertEqual(rev.status, 'IFA')

        rev = self.document.metadata.get_revision(4)
        self.assertIsNotNone(rev)
        self.assertEqual(rev.status, 'FIN')
