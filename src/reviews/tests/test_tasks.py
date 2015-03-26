# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime

from django.test import TestCase
from django.contrib.contenttypes.models import ContentType

from reviews.tasks import do_batch_import

from documents.models import Document
from categories.factories import CategoryFactory
from documents.factories import DocumentFactory
from accounts.factories import UserFactory


class BatchReviewTests(TestCase):
    def setUp(self):
        self.category = CategoryFactory()
        self.user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category
        )
        self.client.login(email=self.user.email, password='pass')
        self.doc1 = DocumentFactory(
            revision={
                'reviewers': [self.user],
                'leader': self.user,
                'approver': self.user,
                'received_date': datetime.date.today(),
            }
        )
        self.doc2 = DocumentFactory(
            revision={
                'reviewers': [self.user],
                'leader': self.user,
                'approver': self.user,
                'received_date': datetime.date.today(),
            }
        )
        self.doc3 = DocumentFactory(
            revision={
                'reviewers': [],
                'leader': None,
                'approver': None,
                'received_date': datetime.date.today(),
            }
        )
        self.content_type = ContentType.objects.get_for_model(self.doc3.metadata)
        self.ok = 'The review started for the following documents'
        self.nok = "We failed to start the review for the following documents"

    def test_batch_review_documents_success(self):
        self.assertFalse(self.doc1.metadata.latest_revision.is_under_review())
        self.assertFalse(self.doc2.metadata.latest_revision.is_under_review())

        do_batch_import.delay(
            self.user.id,
            self.content_type.id,
            [self.doc1.id, self.doc2.id])

        doc1 = Document.objects.get(pk=self.doc1.pk)
        self.assertTrue(doc1.metadata.latest_revision.is_under_review())

        doc2 = Document.objects.get(pk=self.doc2.pk)
        self.assertTrue(doc2.metadata.latest_revision.is_under_review())

    def test_batch_review_errors(self):
        self.assertFalse(self.doc3.metadata.latest_revision.is_under_review())

        do_batch_import.delay(
            self.user.id,
            self.content_type.id,
            [self.doc3.id])

        doc3 = Document.objects.get(pk=self.doc3.pk)
        self.assertFalse(doc3.metadata.latest_revision.is_under_review())

    def test_batch_review_half_success(self):
        self.assertFalse(self.doc1.metadata.latest_revision.is_under_review())
        self.assertFalse(self.doc3.metadata.latest_revision.is_under_review())

        do_batch_import.delay(
            self.user.id,
            self.content_type.id,
            [self.doc1.id, self.doc3.id])

        doc1 = Document.objects.get(pk=self.doc1.pk)
        self.assertTrue(doc1.metadata.latest_revision.is_under_review())

        doc3 = Document.objects.get(pk=self.doc3.pk)
        self.assertFalse(doc3.metadata.latest_revision.is_under_review())
