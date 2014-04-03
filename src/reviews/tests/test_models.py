import datetime

from django.test import TestCase

from categories.factories import CategoryFactory
from documents.factories import DocumentFactory
from accounts.factories import UserFactory


class ReviewMixinTests(TestCase):

    def setUp(self):
        self.category = CategoryFactory()
        self.user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category
        )

    def test_new_doc_cannot_be_reviewed(self):
        doc = DocumentFactory(category=self.category)
        self.assertFalse(doc.latest_revision.can_be_reviewed())

    def test_doc_without_reviewers_cannot_be_reviewed(self):
        doc = DocumentFactory(category=self.category)
        revision = doc.latest_revision
        revision.leader = self.user
        revision.approver = self.user
        revision.save()

        self.assertFalse(revision.can_be_reviewed())

    def test_doc_can_be_reviewed(self):
        doc = DocumentFactory(category=self.category)
        revision = doc.latest_revision
        revision.leader = self.user
        revision.approver = self.user
        revision.reviewers.add(self.user)
        revision.save()

        self.assertTrue(revision.can_be_reviewed())

    def test_doc_can_only_be_reviewed_once(self):
        doc = DocumentFactory(category=self.category)
        revision = doc.latest_revision
        revision.leader = self.user
        revision.approver = self.user
        revision.reviewers.add(self.user)
        revision.review_start_date = datetime.date.today()
        revision.save()

        self.assertFalse(revision.can_be_reviewed())

    def test_start_review_process(self):
        doc = DocumentFactory(category=self.category)
        revision = doc.latest_revision
        revision.leader = self.user
        revision.approver = self.user
        revision.reviewers.add(self.user)
        revision.save()

        self.assertIsNone(revision.review_start_date)
        self.assertIsNone(revision.review_due_date)

        revision.start_review()
        today = datetime.date.today()
        in_two_weeks = today + datetime.timedelta(days=14)

        self.assertEqual(revision.review_start_date, today)
        self.assertEqual(revision.review_due_date, in_two_weeks)
