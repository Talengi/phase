# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.contrib.contenttypes.models import ContentType

from accounts.factories import UserFactory
from categories.factories import CategoryFactory
from default_documents.models import ContractorDeliverable
from distriblists.forms import DistributionListForm


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

    def test_reviewers_not_in_categories(self):
        form = DistributionListForm({
            'name': 'test',
            'categories': [self.category.id],
            'leader': self.users[0].id,
            'reviewers': [UserFactory().id, UserFactory().id]
        })
        self.assertFalse(form.is_valid())
        self.assertTrue('reviewers' in form.errors)
