# -*- coding: utf8 -*-

from __future__ import unicode_literals

from django.test import TestCase
from django.core.management import call_command
from django.test.utils import override_settings

from mock import patch

from accounts.factories import UserFactory
from categories.factories import CategoryFactory
from documents.utils import save_document_forms
from search.signals import connect_signals
from default_documents.forms import DemoMetadataForm, DemoMetadataRevisionForm


@override_settings(ELASTIC_AUTOINDEX=True)
class SignalTests(TestCase):
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
        connect_signals()
        call_command('delete_index')
        call_command('create_index')
        call_command('set_mappings')

    @patch('search.signals.put_category_mapping.delay')
    def test_new_category_mapping_are_created(self, index_mock):
        CategoryFactory()
        self.assertEqual(index_mock.call_count, 1)

    @patch('search.signals.index_document')
    def test_created_document_is_indexed(self, index_mock):
        form = DemoMetadataForm({
            'title': 'Title',
        }, category=self.category)
        rev_form = DemoMetadataRevisionForm({
            'docclass': '1',
            'received_date': '2015-01-01',
            'created_on': '2015-01-01',
        }, category=self.category)
        save_document_forms(form, rev_form, self.category)
        self.assertEqual(index_mock.call_count, 1)

    @patch('search.signals.index_document')
    @patch('search.signals.unindex_document')
    def test_deleted_document_is_unindexed(self, index_mock, unindex_mock):
        form = DemoMetadataForm({
            'title': 'Title',
        }, category=self.category)
        rev_form = DemoMetadataRevisionForm({
            'docclass': '1',
            'received_date': '2015-01-01',
            'created_on': '2015-01-01',
        }, category=self.category)
        doc, meta, rev = save_document_forms(form, rev_form, self.category)
        doc.delete()
        self.assertEqual(unindex_mock.call_count, 1)

    @patch('search.signals.index_document')
    def test_updated_document_is_indexed(self, index_mock):
        form = DemoMetadataForm({
            'title': 'Title',
        }, category=self.category)
        rev_form = DemoMetadataRevisionForm({
            'docclass': '1',
            'received_date': '2015-01-01',
            'created_on': '2015-01-01',
        }, category=self.category)
        doc, meta, rev = save_document_forms(form, rev_form, self.category)
        doc.title = 'foobar'
        doc.save()
        self.assertEqual(index_mock.call_count, 2)

    @patch('search.signals.index_document')
    def test_revised_document_is_indexed(self, index_mock):
        form = DemoMetadataForm({
            'title': 'Title',
        }, category=self.category)
        rev_form = DemoMetadataRevisionForm({
            'docclass': '1',
            'received_date': '2015-01-01',
            'created_on': '2015-01-01',
        }, category=self.category)
        doc, meta, rev = save_document_forms(form, rev_form, self.category)
        revision = doc.latest_revision
        revision.pk = None
        revision.save()
        doc.save()
        self.assertEqual(index_mock.call_count, 2)
