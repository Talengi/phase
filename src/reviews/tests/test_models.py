# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.test import TestCase
from django.utils import timezone

from categories.factories import CategoryFactory
from documents.factories import DocumentFactory
from accounts.factories import UserFactory
from reviews.models import Review


class ReviewMixinTests(TestCase):

    def setUp(self):
        self.category = CategoryFactory()
        self.user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category)
        self.user2 = UserFactory(
            email='user2@phase.fr',
            password='pass',
            category=self.category)
        self.user3 = UserFactory(
            email='user3@phase.fr',
            password='pass',
            category=self.category)

    def assertSameDay(self, datetime1, datetime2):
        def toDate(dt):
            if isinstance(dt, datetime.datetime):
                res = dt.date()
            else:
                res = dt
            return res

        date1 = toDate(datetime1)
        date2 = toDate(datetime2)
        return self.assertEqual(date1, date2)

    def create_reviewable_document(self):
        doc = DocumentFactory(
            category=self.category,
            revision={
                'reviewers': [self.user2],
                'leader': self.user,
                'approver': self.user3,
                'received_date': datetime.datetime.today(),
            }
        )
        return doc.latest_revision

    def create_leader_only_document(self):
        doc = DocumentFactory(
            category=self.category,
            revision={
                'leader': self.user,
                'received_date': datetime.datetime.today(),
            }
        )
        return doc.latest_revision

    def test_new_doc_cannot_be_reviewed(self):
        doc = DocumentFactory(category=self.category)
        self.assertFalse(doc.latest_revision.can_be_reviewed)

    def test_doc_without_leader_cannot_be_reviewed(self):
        doc = DocumentFactory(category=self.category)
        revision = doc.latest_revision
        revision.approver = self.user
        revision.reviewers = [self.user]
        revision.save()

        self.assertFalse(revision.can_be_reviewed)

    def test_doc_with_leader_can_be_reviewed(self):
        revision = self.create_leader_only_document()

        self.assertTrue(revision.can_be_reviewed)

    def test_doc_can_only_be_reviewed_once(self):
        revision = self.create_reviewable_document()
        revision.review_start_date = datetime.date.today()
        revision.save()

        self.assertFalse(revision.can_be_reviewed)

    def test_start_review_process(self):
        revision = self.create_reviewable_document()
        self.assertIsNone(revision.review_start_date)
        self.assertIsNone(revision.review_due_date)
        self.assertIsNone(revision.review_end_date)
        self.assertIsNone(revision.reviewers_step_closed)
        self.assertIsNone(revision.leader_step_closed)

        revision.start_review()
        today = timezone.now().date()
        in_two_weeks = today + datetime.timedelta(days=13)

        self.assertSameDay(revision.review_start_date, today)
        self.assertSameDay(revision.review_due_date, in_two_weeks)

    def test_start_review_at_custom_date(self):
        revision = self.create_reviewable_document()
        self.assertIsNone(revision.review_start_date)

        in_a_month = datetime.date.today() + datetime.timedelta(days=30)

        revision.start_review(at_date=in_a_month)

        self.assertEqual(revision.review_start_date, in_a_month)

    def test_start_review_with_custom_due_date(self):
        revision = self.create_reviewable_document()
        self.assertIsNone(revision.review_start_date)

        in_a_month = datetime.date.today() + datetime.timedelta(days=30)
        two_days_after = in_a_month + datetime.timedelta(days=2)

        revision.start_review(at_date=in_a_month, due_date=two_days_after)

        self.assertEqual(revision.review_start_date, in_a_month)
        self.assertEqual(revision.review_due_date, two_days_after)

    def test_start_review_creates_review_objects(self):
        revision = self.create_reviewable_document()
        revision.reviewers.add(
            UserFactory(),
            UserFactory(),
            UserFactory(),
            UserFactory(),
            UserFactory(),
        )

        reviews = revision.get_reviews()
        self.assertEqual(len(reviews), 0)

        revision.start_review()
        reviews = revision.get_reviews()
        self.assertEqual(len(reviews), 8)

    def test_new_reviews_statuses(self):
        revision = self.create_reviewable_document()
        revision.reviewers.add(
            UserFactory(),
            UserFactory())

        revision.start_review()

        reviewer_review = revision.get_review(self.user2)
        self.assertEqual(reviewer_review.status, 'progress')

        leader_review = revision.get_leader_review()
        self.assertEqual(leader_review.status, 'pending')

        approver_review = revision.get_approver_review()
        self.assertEqual(approver_review.status, 'pending')

    def test_start_leader_only_review(self):
        revision = self.create_leader_only_document()

        revision.start_review()
        self.assertIsNotNone(revision.reviewers_step_closed)
        self.assertIsNone(revision.leader_step_closed)

        reviews = revision.get_reviews()
        self.assertEqual(len(reviews), 1)

        leader_review = revision.get_leader_review()
        self.assertEqual(leader_review.status, 'progress')

    def test_cancel_review(self):
        revision = self.create_reviewable_document()
        revision.start_review()

        reviews = Review.objects.filter(document=revision.document)
        self.assertTrue(reviews.count() > 0)

        revision.cancel_review()
        reviews = Review.objects.filter(document=revision.document)
        self.assertEqual(reviews.count(), 0)
        self.assertIsNone(revision.review_start_date)
        self.assertIsNone(revision.review_due_date)
        self.assertIsNone(revision.review_end_date)
        self.assertIsNone(revision.reviewers_step_closed)
        self.assertIsNone(revision.leader_step_closed)

    def test_end_reviewers_step(self):
        revision = self.create_reviewable_document()
        revision.start_review()

        revision.end_reviewers_step()
        today = timezone.now().date()
        self.assertSameDay(revision.reviewers_step_closed, today)

        reviewer_review = revision.get_review(self.user2)
        self.assertEqual(reviewer_review.status, 'not_reviewed')

        leader_review = revision.get_leader_review()
        self.assertEqual(leader_review.status, 'progress')

        approver_review = revision.get_approver_review()
        self.assertEqual(approver_review.status, 'pending')

    def test_end_reviewers_step_with_reviews(self):
        revision = self.create_reviewable_document()
        revision.start_review()

        reviewer_review = revision.get_review(self.user2)
        self.assertEqual(reviewer_review.status, 'progress')
        reviewer_review.post_review(comments=None)

        revision.end_reviewers_step()

        reviewer_review = revision.get_review(self.user2)
        self.assertEqual(reviewer_review.status, 'reviewed')

        leader_review = revision.get_leader_review()
        self.assertEqual(leader_review.status, 'progress')

        approver_review = revision.get_approver_review()
        self.assertEqual(approver_review.status, 'pending')

    def test_end_reviewers_step_with_mixed_reviewes(self):
        user2 = UserFactory()
        revision = self.create_reviewable_document()
        revision.reviewers.add(user2)
        revision.start_review()

        user1_review = revision.get_review(self.user2)
        user1_review.post_review(None)

        revision.end_reviewers_step()

        user1_review = revision.get_review(self.user2)
        self.assertEqual(user1_review.status, 'reviewed')

        user2_review = revision.get_review(user2)
        self.assertEqual(user2_review.status, 'not_reviewed')

    def test_end_leader_step(self):
        revision = self.create_reviewable_document()
        revision.start_review()
        revision.end_leader_step()

        today = timezone.now().date()
        self.assertSameDay(revision.reviewers_step_closed, today)
        self.assertSameDay(revision.leader_step_closed, today)

        reviewer_review = revision.get_review(self.user2)
        self.assertEqual(reviewer_review.status, 'not_reviewed')

        leader_review = revision.get_leader_review()
        self.assertEqual(leader_review.status, 'not_reviewed')

        approver_review = revision.get_approver_review()
        self.assertEqual(approver_review.status, 'progress')

    def test_end_leader_step_with_review(self):
        revision = self.create_reviewable_document()
        revision.start_review()
        revision.end_reviewers_step()

        leader_review = revision.get_leader_review()
        self.assertEqual(leader_review.status, 'progress')
        leader_review.post_review(comments=None)
        self.assertEqual(leader_review.status, 'reviewed')

        revision.end_leader_step()

        leader_review = revision.get_leader_review()
        self.assertEqual(leader_review.status, 'reviewed')

        approver_review = revision.get_approver_review()
        self.assertEqual(approver_review.status, 'progress')

    def test_end_leader_step_with_reviewers_step_open(self):
        revision = self.create_reviewable_document()
        today = timezone.now().date()
        yesterday = today - datetime.timedelta(days=1)
        revision.review_start_date = yesterday
        revision.end_leader_step()

        self.assertSameDay(revision.reviewers_step_closed, today)
        self.assertSameDay(revision.leader_step_closed, today)

    def test_end_leader_step_with_no_approver(self):
        revision = self.create_leader_only_document()
        today = timezone.now().date()
        revision.start_review()
        revision.end_leader_step()
        self.assertSameDay(revision.leader_step_closed, today)
        self.assertSameDay(revision.review_end_date, today)

    def test_send_back_to_leader_step(self):
        revision = self.create_reviewable_document()
        revision.start_review()
        revision.end_leader_step()
        revision.send_back_to_leader_step()

        self.assertIsNone(revision.leader_step_closed)
        review = revision.get_review(self.user)
        self.assertIsNone(review.closed_on)
        self.assertEqual(review.status, 'progress')

    def test_end_review_process(self):
        revision = self.create_reviewable_document()

        revision.start_review()
        revision.end_review()

        today = timezone.now().date()
        self.assertSameDay(revision.reviewers_step_closed, today)
        self.assertSameDay(revision.leader_step_closed, today)
        self.assertSameDay(revision.review_end_date, today)

        reviewer_review = revision.get_review(self.user2)
        self.assertEqual(reviewer_review.status, 'not_reviewed')

        leader_review = revision.get_leader_review()
        self.assertEqual(leader_review.status, 'not_reviewed')

        approver_review = revision.get_approver_review()
        self.assertEqual(approver_review.status, 'not_reviewed')

    def test_is_under_review(self):
        doc = DocumentFactory(category=self.category)
        revision = doc.latest_revision
        revision.leader = self.user
        revision.approver = self.user3
        revision.reviewers.add(self.user2)
        revision.received_date = datetime.datetime.now()
        revision.save()

        self.assertFalse(revision.is_under_review())

        revision.start_review()
        self.assertTrue(revision.is_under_review())

        revision.end_review()
        self.assertFalse(revision.is_under_review())

    def test_is_overdue(self):
        doc = DocumentFactory(category=self.category)
        revision = doc.latest_revision
        revision.leader = self.user
        revision.save()

        # Review has not started yet
        self.assertFalse(revision.is_overdue())

        # Due date is in the future
        revision.start_review()
        today = timezone.now().date()
        revision.review_due_date = today + datetime.timedelta(days=1)
        self.assertFalse(revision.is_overdue())

        # Due date is today
        revision.review_due_date = today
        self.assertFalse(revision.is_overdue())

        # Due date is in the past
        revision.review_due_date = today - datetime.timedelta(days=1)
        self.assertTrue(revision.is_overdue())

        # Review has ended
        revision.review_due_date = today - datetime.timedelta(days=1)
        revision.end_review()
        self.assertFalse(revision.is_overdue())

    def test_current_step(self):
        revision = self.create_reviewable_document()

        self.assertEqual(revision.current_review_step(), 'pending')

        revision.start_review()
        self.assertEqual(revision.current_review_step(), 'reviewer')

        revision.end_reviewers_step()
        self.assertEqual(revision.current_review_step(), 'leader')

        revision.end_leader_step()
        self.assertEqual(revision.current_review_step(), 'approver')

        revision.end_review()
        self.assertEqual(revision.current_review_step(), 'closed')

    def test_amended_review(self):
        """User can amend their review comments."""
        revision = self.create_reviewable_document()
        revision.start_review()

        review = revision.get_review(self.user)
        review.post_review(comments=None, return_code='1')

        self.assertIsNotNone(review.closed_on)
        self.assertIsNone(review.amended_on)
        self.assertEqual(review.return_code, '1')

        reviewed_on = review.closed_on

        review.post_review(comments=None, return_code='2')
        self.assertEqual(review.closed_on, reviewed_on)
        self.assertIsNotNone(review.amended_on)
        self.assertEqual(review.return_code, '2')
