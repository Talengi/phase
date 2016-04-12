# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.core.urlresolvers import reverse

from categories.factories import CategoryFactory
from documents.factories import DocumentFactory
from accounts.factories import UserFactory


class AlertNewDocumentTests(TestCase):
    def setUp(self):
        self.category = CategoryFactory()
        self.user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category
        )
        self.client.login(email=self.user.email, password='pass')
        self.url = reverse('alert_new_document', args=[
            self.category.organisation.slug,
            self.category.slug,
        ])
        DocumentFactory(
            title='document 1',
            category=self.category,
        )

    def test_single_document(self):
        res = self.client.get(self.url)
        self.assertContains(res, 'document 1')

    def test_many_documents(self):
        res = self.client.get(self.url)
        self.assertNotContains(res, 'document 2')
        self.assertNotContains(res, 'document 3')

        DocumentFactory(
            title='document 2',
            category=self.category,
        )
        DocumentFactory(
            title='document 3',
            category=self.category,
        )

        res = self.client.get(self.url)
        self.assertContains(res, 'document 2')
        self.assertContains(res, 'document 3')
