# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.contrib.contenttypes.models import ContentType

from default_documents.tests.test import ContractorDeliverableTestCase
from categories.factories import CategoryFactory
from accounts.factories import UserFactory
from transmittals.utils import create_transmittal
from transmittals.models import OutgoingTransmittal
from transmittals import errors


class TransmittalCreationTests(ContractorDeliverableTestCase):

    def setUp(self):
        super(TransmittalCreationTests, self).setUp()
        Model = ContentType.objects.get_for_model(OutgoingTransmittal)
        self.dst_category = CategoryFactory(
            category_template__metadata_model=Model)
        self.user1 = UserFactory(
            email='user1@phase.fr',
            password='pass',
            category=self.category)
        self.user2 = UserFactory(
            email='user2@phase.fr',
            password='pass',
            category=self.category)
        self.user3 = UserFactory(
            email='user3@phase.fr',
            password='pass',
            category=self.category)

    def create_docs(self, nb_docs=10, transmittable=True):
        doc_kwargs = {
            'revision': {
                'reviewers': [self.user1],
                'leader': self.user2,
                'approver': self.user3,
                'received_date': datetime.datetime.today()}}

        docs = [self.create_doc(**doc_kwargs) for _ in xrange(nb_docs)]
        revisions = []
        for doc in docs:
            revision = doc.get_metadata().latest_revision
            if transmittable:
                revision.start_review()
                revision.end_review()
            revisions.append(revision)
        return revisions

    def test_create_empty_transmittal(self):
        """A trs cannot be created without revisions."""
        with self.assertRaises(errors.MissingRevisionsError):
            create_transmittal(self.category, self.dst_category, [])

    def test_create_trs_with_invalid_revisions(self):
        """We must check that the given revisions are valid."""
        with self.assertRaises(errors.InvalidRevisionsError):
            revisions = ['toto', 'tata', 'tutu']
            create_transmittal(self.category, self.dst_category, revisions)

    def test_create_trs_with_unreviewed_revisions(self):
        """Revisions must have been reviewed to be transmittable."""
        revisions = self.create_docs(transmittable=False)
        with self.assertRaises(errors.InvalidRevisionsError):
            create_transmittal(self.category, self.dst_category, revisions)

    def test_create_trs_with_invalid_from_category(self):
        """Source category must contain transmittable documents."""
        invalid_cat = CategoryFactory()
        revisions = self.create_docs()
        with self.assertRaises(errors.InvalidCategoryError):
            create_transmittal(invalid_cat, self.dst_category, revisions)

    def test_create_trs_with_invalid_dest_category(self):
        """Destination category must contain outgoing transmittals."""
        invalid_cat = CategoryFactory()
        revisions = self.create_docs()
        with self.assertRaises(errors.InvalidCategoryError):
            create_transmittal(self.category, invalid_cat, revisions)

    def test_create_transmittal(self):
        revisions = self.create_docs()
        transmittal = create_transmittal(
            self.category, self.dst_category, revisions)
        self.assertIsNotNone(transmittal)
        self.assertTrue(isinstance(transmittal, OutgoingTransmittal))
