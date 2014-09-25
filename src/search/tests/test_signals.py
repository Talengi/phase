# -*- coding: utf8 -*-

from __future__ import unicode_literals

from django.test import TestCase
from django.db.models.signals import post_save

from mock import MagicMock, patch
from elasticsearch import Elasticsearch

from accounts.factories import UserFactory
from categories.factories import CategoryFactory
from documents.models import Document
from documents.factories import DocumentFactory
from search.signals import update_index


ElasticMock = MagicMock(Elasticsearch)


class SignalsTests(TestCase):
    def setUp(self):
        self.category = CategoryFactory()
        user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category,
        )
        self.client.login(email=user.email, password='pass')

        # Since test settings disable auto indexing, we need to
        # manually connect the signal here
        post_save.connect(update_index, sender=Document, dispatch_uid='update_index')

    @patch('search.signals.index_document')
    def test_created_document_is_indexed(self, index_mock):
        DocumentFactory(
            category=self.category,
            document_key='FAC09001-FWF-000-HSE-REP-0004',
        )
        self.assertEqual(index_mock.call_count, 1)

    def test_deleted_document_is_unindexed(self):
        pass

    @patch('search.signals.index_document')
    def test_updated_document_is_indexed(self, index_mock):
        doc = DocumentFactory(
            category=self.category,
            document_key='FAC09001-FWF-000-HSE-REP-0004',
        )
        doc.title = 'foobar'
        doc.save()
        self.assertEqual(index_mock.call_count, 2)

    @patch('search.signals.index_document')
    def test_revised_document_is_indexed(self, index_mock):
        doc = DocumentFactory(
            category=self.category,
            document_key='FAC09001-FWF-000-HSE-REP-0004',
        )
        revision = doc.latest_revision
        revision.pk = None
        revision.save()
        doc.save()
        self.assertEqual(index_mock.call_count, 2)
