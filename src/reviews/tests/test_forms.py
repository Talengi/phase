# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from documents.factories import DocumentFactory
from accounts.factories import UserFactory
from categories.factories import CategoryFactory
from default_documents.factories import (
    ContractorDeliverableFactory, ContractorDeliverableRevisionFactory)
from default_documents.models import ContractorDeliverable
from default_documents.forms import ContractorDeliverableRevisionForm


class ReviewFormMixinTest(TestCase):

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
