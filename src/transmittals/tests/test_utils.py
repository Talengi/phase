# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from documents.factories import DocumentFactory
from default_documents.tests.test import ContractorDeliverableTestCase
from categories.factories import CategoryFactory
from accounts.factories import UserFactory, EntityFactory
from transmittals.factories import (
    OutgoingTransmittalFactory, OutgoingTransmittalRevisionFactory)
from transmittals.utils import create_transmittal, find_next_trs_number
from transmittals.models import OutgoingTransmittal
from transmittals import errors


class TransmittalCreationTests(ContractorDeliverableTestCase):
    fixtures = ['initial_values_lists']

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
                'trs_return_code': '1',
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
            create_transmittal(
                self.category, self.dst_category, [], 'FAC10005',
                self.entity)

    def test_create_trs_with_invalid_revisions(self):
        """We must check that the given revisions are valid."""
        with self.assertRaises(errors.InvalidRevisionsError):
            revisions = ['toto', 'tata', 'tutu']
            create_transmittal(
                self.category, self.dst_category, revisions, 'FAC10005',
                self.entity)

    def test_create_trs_with_unreviewed_revisions(self):
        """Revisions must have been reviewed to be transmittable."""
        revisions = self.create_docs(transmittable=False)
        with self.assertRaises(errors.InvalidRevisionsError):
            create_transmittal(
                self.category, self.dst_category, revisions, 'FAC10005',
                self.entity)

    def test_create_trs_with_invalid_from_category(self):
        """Source category must contain transmittable documents."""
        invalid_cat = CategoryFactory()
        revisions = self.create_docs()
        with self.assertRaises(errors.InvalidCategoryError):
            create_transmittal(
                invalid_cat, self.dst_category, revisions, 'FAC10005',
                self.entity)

    def test_create_trs_with_invalid_dest_category(self):
        """Destination category must contain outgoing transmittals."""
        invalid_cat = CategoryFactory()
        revisions = self.create_docs()
        with self.assertRaises(errors.InvalidCategoryError):
            create_transmittal(
                self.category, invalid_cat, revisions, 'FAC10005',
                self.entity)

    def test_create_transmittal(self):
        revisions = self.create_docs()
        revision = revisions[0]
        self.assertIsNone(revision.transmittal)
        self.assertIsNone(revision.external_review_due_date)

        doc, trs, trs_rev = create_transmittal(
            self.category, self.dst_category, revisions, 'FAC10005',
            self.entity)
        self.assertIsNotNone(trs)
        self.assertTrue(isinstance(trs, OutgoingTransmittal))
        self.assertEqual(trs.revisions_category, self.category)

        revision.refresh_from_db()
        self.assertIsNotNone(revision.transmittal)
        self.assertIsNotNone(revision.external_review_due_date)


class TransmittalSequentialNumberTests(TestCase):
    def setUp(self):
        Model = ContentType.objects.get_for_model(OutgoingTransmittal)
        self.category = CategoryFactory(category_template__metadata_model=Model)
        self.entity = EntityFactory()
        self.user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category)
        self.client.login(email=self.user.email, password='pass')

    def create_transmittal(self, sequential_number, **kwargs):
        kwargs.update({
            'category': self.category,
            'metadata': {
                'originator': 'CTR',
                'recipient': self.entity,
                'contract_number': 'FAC10005',
                'sequential_number': sequential_number,
            },
            'metadata_factory_class': OutgoingTransmittalFactory,
            'revision_factory_class': OutgoingTransmittalRevisionFactory,
        })
        doc = DocumentFactory(**kwargs)
        return doc

    def test_seq_nb_with_no_transmittal(self):
        """If no trs exists, the first available seq nb is 1."""
        seq_nb = find_next_trs_number('CTR', self.entity, 'FAC10005')
        self.assertEqual(seq_nb, 1)

    def test_seq_nb_with_existing_transmittals(self):
        """If some trs exist, the first available seq nb is the next one."""
        for nb in range(5):
            self.create_transmittal(nb + 1)

        seq_nb = find_next_trs_number('CTR', self.entity, 'FAC10005')
        self.assertEqual(seq_nb, 6)

    def test_seq_nb_with_hole_in_numbers(self):
        """If there is a hole in the seq numbers, the first available nb is
        still the next one."""
        self.create_transmittal(1)
        self.create_transmittal(2)
        self.create_transmittal(5)
        self.create_transmittal(8)

        seq_nb = find_next_trs_number('CTR', self.entity, 'FAC10005')
        self.assertEqual(seq_nb, 9)
