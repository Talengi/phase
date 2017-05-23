# -*- coding: utf-8 -*-

from collections import OrderedDict

from django.test import TestCase
from django.contrib.contenttypes.models import ContentType

from accounts.factories import UserFactory
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
        self.revisions = [doc.get_latest_revision() for doc in self.docs]

    def test_csv_formatter(self):
        fields = OrderedDict((
            ('Document Number', 'document_key'),
            ('Title', 'title'),
        ))
        formatter = CSVFormatter(fields)
        csv = formatter.format(self.revisions[0:2])
        expected_csv = '{};{}\n{};{}\n'.format(
            self.docs[0].document_key,
            self.docs[0].title,
            self.docs[1].document_key,
            self.docs[1].title,
        ).encode()
        self.assertEqual(csv, expected_csv)

    def test_csv_formatter_foreign_key(self):
        fields = {
            'Document Number': 'document_key',
            'Leader': 'leader',
        }
        formatter = CSVFormatter(fields)
        metadata = self.docs[0].metadata
        revision = metadata.latest_revision
        revision.leader = UserFactory(name='Grand Schtroumpf')
        revision.save()
        csv = formatter.format([revision])
        expected_csv = '{};Grand Schtroumpf\n'.format(metadata.document_key).encode()
        self.assertEqual(csv, expected_csv)
