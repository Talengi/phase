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
        UserFactory(email='user6@test.com')

        self.other_category = CategoryFactory()
        self.other_category.users.add(*self.users)

    def test_successful_import(self):
        """Importing the file creates the distribution lists."""
        qs = DistributionList.objects.all()
        self.assertEqual(qs.count(), 0)

        xls_file = os.path.join(
            os.path.dirname(__file__),
            'fixtures',
            'valid_distrib_list.xlsx')
        import_lists(xls_file, self.category)

        self.assertEqual(qs.count(), 5)

        self.assertEqual(qs[0].name, 'Liste 1')
        self.assertEqual(qs[0].leader.email, 'user3@test.com')
        self.assertEqual(qs[0].approver.email, 'user5@test.com')
        self.assertEqual(qs[0].reviewers.count(), 2)

        self.assertEqual(qs[2].name, 'Liste 3')
        self.assertEqual(qs[2].leader.email, 'user5@test.com')
        self.assertIsNone(qs[2].approver)

    def test_importing_twice_with_different_categories(self):
        qs = DistributionList.objects.all()
        self.assertEqual(qs.count(), 0)

        xls_file = os.path.join(
            os.path.dirname(__file__),
            'fixtures',
            'valid_distrib_list.xlsx')
        import_lists(xls_file, self.category)
        import_lists(xls_file, self.other_category)

        self.assertEqual(qs.count(), 5)
        self.assertEqual(len(qs[0].categories.all()), 2)

    def test_import_overrides_existing_content(self):
        """Importing is an idempotent action (PUT, not POST)."""
        qs = DistributionList.objects.all()
        self.assertEqual(qs.count(), 0)

        xls_file = os.path.join(
            os.path.dirname(__file__),
            'fixtures',
            'valid_distrib_list.xlsx')
        import_lists(xls_file, self.category)

        self.assertEqual(qs.count(), 5)

        import_lists(xls_file, self.category)
        self.assertEqual(qs.count(), 5)

        qs[0].delete()
        self.assertEqual(qs.count(), 4)

        import_lists(xls_file, self.category)
        self.assertEqual(qs.count(), 5)

    def test_invalid_data_no_leader(self):
        """Cannot import lists without a leader."""
        qs = DistributionList.objects.all()
        self.assertEqual(qs.count(), 0)

        xls_file = os.path.join(
            os.path.dirname(__file__),
            'fixtures',
            'distrib_list_missing_leader.xlsx')
        import_lists(xls_file, self.category)

        self.assertEqual(qs.count(), 1)

    def test_invalid_data_unknown_user(self):
        """Can only create lists with known users."""
        qs = DistributionList.objects.all()
        self.assertEqual(qs.count(), 0)

        xls_file = os.path.join(
            os.path.dirname(__file__),
            'fixtures',
            'distrib_list_unknown_user.xlsx')
        import_lists(xls_file, self.category)

        self.assertEqual(qs.count(), 1)

    def test_invalid_data_invalid_category(self):
        """Users have to belong to the category."""
        qs = DistributionList.objects.all()
        self.assertEqual(qs.count(), 0)

        xls_file = os.path.join(
            os.path.dirname(__file__),
            'fixtures',
            'distrib_list_wrong_category.xlsx')
        import_lists(xls_file, self.category)

        self.assertEqual(qs.count(), 1)
