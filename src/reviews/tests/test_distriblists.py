# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.test import TestCase

from categories.factories import CategoryFactory
from accounts.factories import UserFactory
from reviews.distriblists import import_lists
from reviews.models import DistributionList


class DistributionListsImportTests(TestCase):
    def setUp(self):
        self.category = CategoryFactory()
        self.users = [
            UserFactory(email='user1@test.com', category=self.category),
            UserFactory(email='user2@test.com', category=self.category),
            UserFactory(email='user3@test.com', category=self.category),
            UserFactory(email='user4@test.com', category=self.category),
            UserFactory(email='user5@test.com', category=self.category),
        ]

    def test_successful_import(self):
        self.assertEqual(DistributionList.objects.all().count(), 0)

        xls_file = os.path.join(
            os.path.dirname(__file__),
            'fixtures',
            'valid_distrib_list.xlsx')
        import_lists(xls_file, self.category)

        qs = DistributionList.objects.all()
        self.assertEqual(qs.count(), 5)

        self.assertEqual(qs[0].name, 'Liste 1')
        self.assertEqual(qs[0].leader.email, 'user3@test.com')
        self.assertEqual(qs[0].approver.email, 'user5@test.com')
        self.assertEqual(qs[0].reviewers.count(), 2)

        self.assertEqual(qs[2].name, 'Liste 3')
        self.assertEqual(qs[2].leader.email, 'user5@test.com')
        self.assertIsNone(qs[2].approver)
