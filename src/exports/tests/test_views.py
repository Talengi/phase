# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.core.urlresolvers import reverse

from categories.factories import CategoryFactory
from accounts.factories import UserFactory
from exports.factories import ExportFactory
from exports.models import Export


class ExportCreateTests(TestCase):
    def setUp(self):
        self.category = CategoryFactory()
        self.user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category)
        self.client.login(email=self.user.email, password='pass')
        self.url = reverse('export_create', args=[
            self.category.organisation.slug, self.category.slug])

    def test_export_create_cleanup_old_exports(self):
        for _ in xrange(0, 25):
            ExportFactory(
                owner=self.user,
                category=self.category)

        self.assertEqual(Export.objects.all().count(), 25)

        self.client.post(self.url)

        self.assertEqual(Export.objects.all().count(), 20)
