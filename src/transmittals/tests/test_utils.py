# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType

from default_documents.tests.test import ContractorDeliverableTestCase
from categories.factories import CategoryFactory
from transmittals.utils import create_transmittal
from transmittals.models import OutgoingTransmittal
from transmittals import errors


class TransmittalCreationTests(ContractorDeliverableTestCase):

    def setUp(self):
        super(TransmittalCreationTests, self).setUp()
        Model = ContentType.objects.get_for_model(OutgoingTransmittal)
        self.dst_category = CategoryFactory(
            category_template__metadata_model=Model)
        docs = [self.create_doc() for _ in xrange(10)]
        self.revisions = [doc.get_metadata().latest_revision for doc in docs]

    def test_create_empty_transmittal(self):
        """A trs cannot be created without revisions."""
        with self.assertRaises(errors.MissingRevisionsError):
            create_transmittal(self.category, self.dst_category, [])

    def test_create_trs_with_invalid_revisions(self):
        """We must check that the given revisions are valid."""
        with self.assertRaises(errors.InvalidRevisionsError):
            revisions = ['toto', 'tata', 'tutu']
            create_transmittal(self.category, self.dst_category, revisions)

    def test_create_transmittal(self):
        transmittal = create_transmittal(
            self.category, self.dst_category, self.revisions)
        self.assertIsNotNone(transmittal)
        self.assertTrue(isinstance(transmittal, OutgoingTransmittal))
