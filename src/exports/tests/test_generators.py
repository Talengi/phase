# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import OrderedDict

from django.test import TestCase, override_settings
from django.contrib.contenttypes.models import ContentType

from mock import MagicMock

from documents.factories import DocumentFactory
from categories.factories import CategoryFactory
from default_documents.factories import (
    ContractorDeliverableFactory, ContractorDeliverableRevisionFactory)
from default_documents.models import ContractorDeliverable
from exports.generators import ExportGenerator, CSVGenerator


class ExportGeneratorTests(TestCase):
    def setUp(self):
        Model = ContentType.objects.get_for_model(ContractorDeliverable)
        self.category = CategoryFactory(category_template__metadata_model=Model)
        self.docs = (
            DocumentFactory(
                metadata_factory_class=ContractorDeliverableFactory,
                revision_factory_class=ContractorDeliverableRevisionFactory,
                category=self.category)
            for i in range(1, 20))

        self.es_mock = MagicMock(return_value=(
            [doc.latest_revision.pk for doc in self.docs],
            20
        ))

    @override_settings(EXPORTS_CHUNK_SIZE=5)
    def test_generator_iterator(self):
        generator = ExportGenerator(self.category, {}, {})
        generator.get_es_results = self.es_mock
        iterator = iter(generator)
        chunk = iterator.next()  # header

        chunk = iterator.next()
        self.assertEqual(chunk.count(), 5)

        chunk = iterator.next()
        self.assertEqual(chunk.count(), 5)

        chunk = iterator.next()
        self.assertEqual(chunk.count(), 5)

        chunk = iterator.next()
        self.assertEqual(chunk.count(), 4)

        with self.assertRaises(StopIteration):
            chunk = iterator.next()

    def test_csv_generator_header(self):
        fields = OrderedDict((
            ('Title', 'title'),
            ('Document number', 'document_key')))
        generator = CSVGenerator(self.category, {}, fields)
        generator.get_es_results = self.es_mock
        iterator = iter(generator)
        chunk = iterator.next()
        self.assertEqual(chunk, [['Title', 'Document number']])
