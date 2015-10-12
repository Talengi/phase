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
from default_documents.factories import (
    ContractorDeliverableFactory, ContractorDeliverableRevisionFactory)


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
