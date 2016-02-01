# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.test import TestCase
from django.contrib.contenttypes.models import ContentType

from accounts.factories import UserFactory
from categories.factories import CategoryFactory
from documents.factories import DocumentFactory
from default_documents.models import ContractorDeliverable
from default_documents.forms import ContractorDeliverableRevisionForm
from default_documents.factories import (ContractorDeliverableFactory,
                                         ContractorDeliverableRevisionFactory)
from reviews.models import Review
from reviews.forms import DistributionListForm


class BaseReviewFormMixinTests(TestCase):
    def setUp(self):
        Model = ContentType.objects.get_for_model(ContractorDeliverable)
        self.category = CategoryFactory(category_template__metadata_model=Model)

        self.user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category)
        self.user2 = UserFactory(
            email='user2@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category)
        self.user3 = UserFactory(
            email='user3@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category)

        self.data = {
            'docclass': 3,
            'purpose_of_issue': 'FR',
            'created_on': '2015-01-01',
            'received_date': '2015-01-01'
        }


class ReviewFormMixinTest(BaseReviewFormMixinTests):

    def test_review_form_is_valid(self):
        form = ContractorDeliverableRevisionForm(self.data, category=self.category)
        self.assertTrue(form.is_valid())

    def test_user_is_both_leader_and_reviewer(self):
        """A single user cannot appear twice in the same distribution list."""
        self.data.update({
            'leader': self.user.id,
            'approver': self.user2.id,
            'reviewers': str(self.user.id),
        })
        form = ContractorDeliverableRevisionForm(self.data, category=self.category)
        self.assertFalse(form.is_valid())

    def test_user_is_both_approver_and_reviewer(self):
        """A single user cannot appear twice in the same distribution list."""
        self.data.update({
            'leader': self.user2.id,
            'approver': self.user.id,
            'reviewers': str(self.user.id),
        })
        form = ContractorDeliverableRevisionForm(self.data, category=self.category)
        self.assertFalse(form.is_valid())

    def test_user_is_both_leader_and_approver(self):
        """A single user cannot appear twice in the same distribution list."""
        self.data.update({
            'leader': self.user.id,
            'approver': self.user.id
        })
        form = ContractorDeliverableRevisionForm(self.data, category=self.category)
        self.assertFalse(form.is_valid())


class UpdateDistribListTests(BaseReviewFormMixinTests):
    """Test distribution list updates during review.

    When reviewers, leader or approver are modified during a review, the
    actual distribution list must be updated accordingly.

    """

    def setUp(self):
        super(UpdateDistribListTests, self).setUp()
        self.user4 = UserFactory(
            email='user4@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category)
        self.doc = DocumentFactory(
            metadata_factory_class=ContractorDeliverableFactory,
            revision_factory_class=ContractorDeliverableRevisionFactory,
            category=self.category,
            revision={
                'reviewers': [self.user],
                'leader': self.user2,
                'approver': self.user3,
                'received_date': datetime.datetime.today(),
            })
        self.rev = self.doc.get_latest_revision()
        self.data.update({
            'reviewers': str(self.user.id),
            'leader': self.user2.id,
            'approver': self.user3.id,
            'review_start_date': datetime.datetime.today(),
            'review_due_date': datetime.datetime.today() + datetime.timedelta(days=14)
        })

    def test_form_is_valid(self):
        form = ContractorDeliverableRevisionForm(
            self.data,
            instance=self.rev,
            category=self.category)
        self.assertTrue(form.is_valid())

    def test_reviewers_cannot_be_added_after_reviewers_step(self):
        self.rev.start_review()
        self.rev.end_reviewers_step()

        reviewers = '{},{}'.format(self.user.id, self.user4.id)
        self.data.update({'reviewers': reviewers})

        form = ContractorDeliverableRevisionForm(
            self.data,
            instance=self.rev,
            category=self.category)
        self.assertFalse(form.is_valid())
        self.assertTrue('reviewers' in form.errors)

    def test_reviewers_cannot_be_deleted_after_reviewers_step(self):
        self.rev.start_review()
        self.rev.end_reviewers_step()
        self.data.update({'reviewers': ''})
        form = ContractorDeliverableRevisionForm(
            self.data,
            instance=self.rev,
            category=self.category)
        self.assertFalse(form.is_valid())
        self.assertTrue('reviewers' in form.errors)

    def test_reviewer_can_be_added_during_reviewers_step(self):
        self.rev.start_review()

        # Count initial Reviews
        qs = Review.objects \
            .filter(document=self.rev.document) \
            .filter(revision=self.rev.revision) \
            .filter(role='reviewer')
        self.assertEqual(qs.count(), 1)

        # Add a reviewer
        reviewers = '{},{}'.format(self.user.id, self.user4.id)
        self.data.update({'reviewers': reviewers})
        form = ContractorDeliverableRevisionForm(
            self.data,
            instance=self.rev,
            category=self.category)
        self.assertTrue(form.is_valid())
        form.save()

        # Count updated Reviews
        self.assertEqual(qs.count(), 2)

    def test_reviewer_may_be_deleted_during_reviewers_step(self):
        """A reviewer can be deleted if they didn't submit a review yet."""
        self.rev.start_review()

        # Count initial Reviews
        qs = Review.objects \
            .filter(document=self.rev.document) \
            .filter(revision=self.rev.revision) \
            .filter(role='reviewer')
        self.assertEqual(qs.count(), 1)

        # Remove a reviewer
        reviewers = ''
        self.data.update({'reviewers': reviewers})
        form = ContractorDeliverableRevisionForm(
            self.data,
            instance=self.rev,
            category=self.category)
        self.assertTrue(form.is_valid())
        form.save()

        # Count updated Reviews
        self.assertEqual(qs.count(), 0)

    def test_reviewer_may_not_be_deleted_during_reviewers_step(self):
        """Reviewers that submitted a review cannot be removed."""
        self.rev.reviewers.add(self.user4)
        self.rev.start_review()

        # Post a review
        review = self.rev.get_review(self.user)
        review.post_review(comments=None)

        # Assert the reviewers stop is still open
        self.rev.refresh_from_db()
        self.assertIsNone(self.rev.reviewers_step_closed)

        # Try to remove the initial reviewer
        reviewers = str(self.user4.id)
        self.data.update({'reviewers': reviewers})
        form = ContractorDeliverableRevisionForm(
            self.data,
            instance=self.rev,
            category=self.category)
        self.assertFalse(form.is_valid())
        self.assertTrue('reviewers' in form.errors)

    def test_removing_reviewers_can_end_reviewers_step(self):
        """Remove all reviewers, and the review goes up to leader step."""
        self.rev.reviewers.add(self.user4)
        self.rev.start_review()

        leader_review = self.rev.get_review(self.user2)
        self.assertEqual(leader_review.status, 'pending')

        # Count Review objects
        qs = Review.objects \
            .filter(document=self.rev.document) \
            .filter(revision=self.rev.revision) \
            .filter(role='reviewer')
        self.assertEqual(qs.count(), 2)

        # Remove one reviewer
        self.data.update({'reviewers': str(self.user.id)})
        form = ContractorDeliverableRevisionForm(
            self.data,
            instance=self.rev,
            category=self.category)
        self.assertTrue(form.is_valid())
        form.save()

        # Assert the reviewers step is still open
        self.rev.refresh_from_db()
        self.assertIsNone(self.rev.reviewers_step_closed)
        self.assertEqual(qs.count(), 1)

        # Remove second reviewer
        self.data.update({'reviewers': ''})
        form = ContractorDeliverableRevisionForm(
            self.data,
            instance=self.rev,
            category=self.category)
        self.assertTrue(form.is_valid())
        form.save()

        # Assert the reviewers step is closed
        self.rev.refresh_from_db()
        self.assertEqual(qs.count(), 0)
        self.assertIsNotNone(self.rev.reviewers_step_closed)

        leader_review.refresh_from_db()
        self.assertEqual(leader_review.status, 'progress')

    def test_leader_cannot_be_changed_after_leader_step(self):
        self.rev.start_review()
        self.rev.end_leader_step()
        self.data.update({'leader': self.user4.id})

        form = ContractorDeliverableRevisionForm(
            self.data,
            instance=self.rev,
            category=self.category)
        self.assertFalse(form.is_valid())
        self.assertTrue('leader' in form.errors)

    def test_update_leader_updates_distrib_list(self):
        self.rev.start_review()
        review = self.rev.get_review(self.user2)
        self.assertEqual(review.role, 'leader')

        self.data.update({'leader': self.user4.id})
        form = ContractorDeliverableRevisionForm(
            self.data,
            instance=self.rev,
            category=self.category)
        rev = form.save()

        review = rev.get_review(self.user2)
        self.assertIsNone(review)

        review = rev.get_review(self.user4)
        self.assertEqual(review.role, 'leader')

    def test_approver_cannot_be_changed_after_approver_step(self):
        self.rev.start_review()
        self.rev.end_review()
        self.data.update({'approver': self.user4.id})

        form = ContractorDeliverableRevisionForm(
            self.data,
            instance=self.rev,
            category=self.category)
        self.assertFalse(form.is_valid())
        self.assertTrue('approver' in form.errors)

    def test_update_approver_updates_distrib_list(self):
        self.rev.start_review()
        review = self.rev.get_review(self.user3)
        self.assertEqual(review.role, 'approver')

        self.data.update({'approver': self.user4.id})
        form = ContractorDeliverableRevisionForm(
            self.data,
            instance=self.rev,
            category=self.category)
        rev = form.save()

        review = rev.get_review(self.user3)
        self.assertIsNone(review)

        review = rev.get_review(self.user4)
        self.assertEqual(review.role, 'approver')

    def test_removing_approver_during_approver_step_ends_review(self):
        self.rev.start_review()
        self.rev.end_leader_step()

        self.assertIsNone(self.rev.review_end_date)

        self.data.update({'approver': ''})
        form = ContractorDeliverableRevisionForm(
            self.data,
            instance=self.rev,
            category=self.category)
        rev = form.save()

        review = rev.get_review(self.user3)
        self.assertIsNone(review)

        self.assertIsNotNone(self.rev.review_end_date)

    def test_removing_approver_before_approver_step_doesnt_end_review(self):
        self.rev.start_review()

        self.assertIsNone(self.rev.review_end_date)

        self.data.update({'approver': ''})
        form = ContractorDeliverableRevisionForm(
            self.data,
            instance=self.rev,
            category=self.category)
        rev = form.save()

        review = rev.get_review(self.user3)
        self.assertIsNone(review)

        self.assertIsNone(self.rev.review_end_date)


class DistributionListFormTests(TestCase):
    def setUp(self):
        Model = ContentType.objects.get_for_model(ContractorDeliverable)
        self.category = CategoryFactory(category_template__metadata_model=Model)
        self.users = [
            UserFactory(
                email='user%s@phase.fr' % user,
                password='pass',
                category=self.category
            ) for user in range(1, 5)]

    def test_form_valid(self):
        form = DistributionListForm({
            'name': 'test',
            'categories': [self.category.id],
            'leader': self.users[0].id,
            'approver': self.users[1].id,
            'reviewers': [u.id for u in self.users[2:]]})
        self.assertTrue(form.is_valid())

    def test_same_user_in_leader_and_approver(self):
        form = DistributionListForm({
            'name': 'test',
            'categories': [self.category.id],
            'leader': self.users[0].id,
            'approver': self.users[0].id,
            'reviewers': [u.id for u in self.users[2:]]})
        self.assertFalse(form.is_valid())

    def test_same_user_in_leader_and_reviewer(self):
        form = DistributionListForm({
            'name': 'test',
            'categories': [self.category.id],
            'leader': self.users[1].id,
            'approver': self.users[0].id,
            'reviewers': [u.id for u in self.users[1:]]})
        self.assertFalse(form.is_valid())

    def test_same_user_in_approver_and_reviewer(self):
        form = DistributionListForm({
            'name': 'test',
            'categories': [self.category.id],
            'leader': self.users[0].id,
            'approver': self.users[1].id,
            'reviewers': [u.id for u in self.users[1:]]})
        self.assertFalse(form.is_valid())

    def test_leader_not_in_categories(self):
        form = DistributionListForm({
            'name': 'test',
            'categories': [self.category.id],
            'leader': UserFactory().id})
        self.assertFalse(form.is_valid())
        self.assertTrue('leader' in form.errors)

    def test_approver_not_in_categories(self):
        form = DistributionListForm({
            'name': 'test',
            'categories': [self.category.id],
            'leader': self.users[0].id,
            'approver': UserFactory().id})
        self.assertFalse(form.is_valid())
        self.assertTrue('approver' in form.errors)
