# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.contrib.contenttypes.models import ContentType

from documents.factories import DocumentFactory
from categories.factories import CategoryFactory
from default_documents.factories import (
    ContractorDeliverableFactory, ContractorDeliverableRevisionFactory)
from default_documents.models import ContractorDeliverable
from exports.formatters import CSVFormatter


class FormatterTests(TestCase):
    def setUp(self):
        Model = ContentType.objects.get_for_model(ContractorDeliverable)
        self.category = CategoryFactory(category_template__metadata_model=Model)
        self.docs = [
            DocumentFactory(
                metadata_factory_class=ContractorDeliverableFactory,
                revision_factory_class=ContractorDeliverableRevisionFactory,
                category=self.category)
            for i in range(1, 20)]

    def test_csv_formatter(self):
        fields = {
            'Document Number': 'document_key',
            'Title': 'title',
        }
        formatter = CSVFormatter(fields)
        csv = formatter.format(self.docs[0:2])
        expected_csv = b'{};{}\n{};{}\n'.format(
            self.docs[0].document_key,
            self.docs[0].title,
            self.docs[1].document_key,
            self.docs[1].title,
        )
        self.assertEqual(csv, expected_csv)
