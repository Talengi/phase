# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.contrib.auth.models import Permission

from rest_framework.test import APITestCase

from categories.factories import CategoryFactory
from accounts.factories import UserFactory


class UserApiAclTests(APITestCase):
    def setUp(self):
        self.category = CategoryFactory()
        self.user = UserFactory(name='user', password='pass', category=self.category)

        self.dc_perms = Permission.objects.filter(codename__endswith='_document')
        self.dc = UserFactory(name='dc', password='pass', category=self.category)
        self.dc.user_permissions = self.dc_perms
        self.dc.save()

        self.url = reverse('user-list', args=[
            self.category.organisation.slug,
            self.category.category_template.slug,
        ])

    def test_anonymous_access_forbidden(self):
        """Anonymous cannot access the user api."""
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 403)

    def test_simple_user_access_forbidden(self):
        """Simple users don't have access to the user api."""
        self.client.login(username=self.user.email, password='pass')

        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 403)

    def test_dc_can_access_user_api(self):
        """Document controllers can access the user api."""
        self.client.login(username=self.dc.email, password='pass')

        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_dc_can_only_access_users_from_his_category(self):
        other_category = CategoryFactory()
        user = UserFactory(name='dc2', password='pass', category=other_category)
        user.user_permissions = self.dc_perms
        user.save()
        self.client.login(username=user.email, password='pass')

        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 403)

    def test_dc_cannot_see_users_from_other_categories(self):
        other_category = CategoryFactory()
        user1 = UserFactory(name='toto', password='pass', category=other_category)
        user1.save()

        user2 = UserFactory(name='tata', password='pass', category=self.category)
        user2.save()

        self.client.login(username=self.dc.email, password='pass')

        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

        self.assertTrue('tata' in res.content)
        self.assertTrue('toto' not in res.content)
