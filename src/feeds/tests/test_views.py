# -*- coding: utf-8 -*-


import base64

from django.core.urlresolvers import reverse
from django.test import TestCase

from accounts.factories import UserFactory
from categories.factories import CategoryFactory
from documents.factories import DocumentFactory


class FeedAuthenticationTests(TestCase):
    def setUp(self):
        self.category = CategoryFactory()
        self.user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category
        )
        self.url = reverse('feed_new_documents', args=[
            self.category.organisation.slug,
            self.category.slug,
        ])
        DocumentFactory(
            title='document 1',
            category=self.category,
        )

    def test_authenticated_user(self):
        self.client.login(email=self.user.email, password='pass')
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_unsecure_unauthenticated_user(self):
        res = self.client.get(self.url, **{'wsgi.url_scheme': 'http'})
        self.assertEqual(res.status_code, 403)

    def test_secure_unauthenticated_user(self):
        res = self.client.get(self.url, **{'wsgi.url_scheme': 'https'})
        self.assertEqual(res.status_code, 401)
        self.assertTrue('WWW-AUTHENTICATE' in res)

    def test_login_with_invalid_credentials(self):
        res = self.client.get(self.url, **{
            'wsgi.url_scheme': 'https',
            'HTTP_AUTHORIZATION': 'portenawak'
        })
        self.assertEqual(res.status_code, 403)

    def test_login_unactive_user(self):
        self.user.is_active = False
        self.user.save()

        credentials = '{}:pass'.format(self.user.email)
        b64_credentials = base64.b64encode(credentials)
        full_credentials = 'Basic: {}'.format(b64_credentials)

        res = self.client.get(self.url, **{
            'wsgi.url_scheme': 'https',
            'HTTP_AUTHORIZATION': full_credentials
        })
        self.assertEqual(res.status_code, 401)

    def test_login_with_wrong_password(self):
        credentials = '{}:wrongpassword'.format(self.user.email)
        b64_credentials = base64.b64encode(credentials)
        full_credentials = 'Basic: {}'.format(b64_credentials)

        res = self.client.get(self.url, **{
            'wsgi.url_scheme': 'https',
            'HTTP_AUTHORIZATION': full_credentials
        })
        self.assertEqual(res.status_code, 401)

    def test_sucessfull_login_user(self):
        credentials = '{}:pass'.format(self.user.email)
        b64_credentials = base64.b64encode(credentials)
        full_credentials = 'Basic: {}'.format(b64_credentials)

        res = self.client.get(self.url, **{
            'wsgi.url_scheme': 'https',
            'HTTP_AUTHORIZATION': full_credentials
        })
        self.assertEqual(res.status_code, 200)


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
        self.url = reverse('alert_new_documents', args=[
            self.category.organisation.slug,
            self.category.slug,
        ])
        DocumentFactory(
            title='document 1',
            category=self.category,
            created_by=self.user,
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
        self.assertContains(res, 'document 2')
        self.assertContains(res, self.user.name)
