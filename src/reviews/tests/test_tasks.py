# -*- coding: utf-8 -*-



import datetime

from django.test import TestCase
from django.contrib.contenttypes.models import ContentType

from audit_trail.models import Activity
from reviews.tasks import do_batch_import, batch_cancel_reviews

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
            category=self.category,
            revision={
                'leader': self.user,
                'received_date': datetime.date.today(),
            }
        )
        self.doc2 = DocumentFactory(
            category=self.category,
            revision={
                'leader': self.user,
                'received_date': datetime.date.today(),
            }
        )
        self.doc3 = DocumentFactory(
            category=self.category,
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
            self.category.id,
            self.content_type.id,
            [self.doc1.id, self.doc2.id])

        doc1 = Document.objects.get(pk=self.doc1.pk)
        self.assertTrue(doc1.metadata.latest_revision.is_under_review())

        doc2 = Document.objects.get(pk=self.doc2.pk)
        self.assertTrue(doc2.metadata.latest_revision.is_under_review())

        # Check audit trail
        activities = Activity.objects.order_by('created_on')
        self.assertEqual(activities[0].verb, Activity.VERB_STARTED_REVIEW)
        self.assertEqual(activities[0].target, self.doc1.metadata.latest_revision)
        self.assertEqual(activities[1].verb, Activity.VERB_STARTED_REVIEW)
        self.assertEqual(activities[1].target, self.doc2.metadata.latest_revision)

    def test_batch_review_errors(self):
        self.assertFalse(self.doc3.metadata.latest_revision.is_under_review())
        do_batch_import.delay(
            self.user.id,
            self.category.id,
            self.content_type.id,
            [self.doc3.id])

        doc3 = Document.objects.get(pk=self.doc3.pk)
        self.assertFalse(doc3.metadata.latest_revision.is_under_review())
        # No activity was logged
        self.assertEqual(Activity.objects.count(), 0)

    def test_batch_review_half_success(self):
        self.assertFalse(self.doc1.metadata.latest_revision.is_under_review())
        self.assertFalse(self.doc3.metadata.latest_revision.is_under_review())

        do_batch_import.delay(
            self.user.id,
            self.category.id,
            self.content_type.id,
            [self.doc1.id, self.doc3.id])

        doc1 = Document.objects.get(pk=self.doc1.pk)
        self.assertTrue(doc1.metadata.latest_revision.is_under_review())

        doc3 = Document.objects.get(pk=self.doc3.pk)
        self.assertFalse(doc3.metadata.latest_revision.is_under_review())

    def test_batch_cancel_review(self):
        self.doc1.get_latest_revision().start_review()
        self.doc2.get_latest_revision().start_review()

        self.assertTrue(self.doc1.get_latest_revision().is_under_review())
        self.assertTrue(self.doc2.get_latest_revision().is_under_review())
        self.assertFalse(self.doc3.get_latest_revision().is_under_review())

        batch_cancel_reviews.delay(
            self.user.id,
            self.category.id,
            self.content_type.id,
            [self.doc1.id, self.doc2.id, self.doc3.id])

        doc1 = Document.objects.get(pk=self.doc1.pk)
        doc2 = Document.objects.get(pk=self.doc2.pk)
        doc3 = Document.objects.get(pk=self.doc3.pk)

        self.assertFalse(doc1.get_latest_revision().is_under_review())
        self.assertFalse(doc2.get_latest_revision().is_under_review())
        self.assertFalse(doc3.get_latest_revision().is_under_review())

        # Check audit trail
        activities = Activity.objects.order_by('created_on')
        # Only two reviews were canceled
        self.assertEqual(activities.count(), 2)
        for i, doc in enumerate([doc1, doc2]):
            self.assertEqual(activities[i].verb,
                             Activity.VERB_CANCELLED_REVIEW)
            self.assertEqual(activities[i].target,
                             doc.get_latest_revision())
