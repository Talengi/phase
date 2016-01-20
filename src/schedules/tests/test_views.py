# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.utils.timezone import utc
from django.core.urlresolvers import reverse

from default_documents.tests.test import ContractorDeliverableTestCase
from documents.models import Document


class ScheduleFieldsTests(ContractorDeliverableTestCase):
    """Test automatic filling of "schedule" section fields."""

    fixtures = ['initial_values_lists']

    def setUp(self):
        super(ScheduleFieldsTests, self).setUp()
        self.today = datetime.datetime.today().replace(tzinfo=utc).date()
        self.create_url = reverse('document_create', args=[
            self.category.organisation.slug,
            self.category.slug,
        ])
        self.form_data = {
            'title': 'title',
            'document_number': 'KEY',
            'contract_number': 'FAC09001',
            'originator': 'CTR',
            'unit': '001',
            'discipline': 'PRT',
            'document_type': 'LAY',
            'sequential_number': '0001',
            'docclass': 1,
            'purpose_of_issue': 'FR',
            'created_on': self.today.strftime('%Y-%m-%d'),
            'received_date': self.today.strftime('%Y-%m-%d'),
            'status': '',
        }

    def test_create_doc_with_empty_status(self):
        self.client.post(self.create_url, self.form_data, follow=True)

        doc = Document.objects.get(document_key='KEY')
        meta = doc.get_metadata()
        self.assertIsNone(meta.status_std_actual_date)

        rev = meta.latest_revision
        self.assertEqual(rev.status, '')

    def test_create_doc_with_status(self):
        self.form_data.update({'status': 'STD'})
        self.client.post(self.create_url, self.form_data, follow=True)
        doc = Document.objects.get(document_key='KEY')

        meta = doc.get_metadata()
        self.assertEqual(meta.status_std_actual_date, self.today)
        self.assertIsNone(meta.status_ifa_actual_date)

    def test_create_doc_with_different_status(self):
        self.form_data.update({'status': 'IFA'})
        self.client.post(self.create_url, self.form_data, follow=True)
        doc = Document.objects.get(document_key='KEY')

        meta = doc.get_metadata()
        self.assertIsNone(meta.status_std_actual_date)
        self.assertEqual(meta.status_ifa_actual_date, self.today)

    def test_edit_revision_with_a_status(self):
        self.client.post(self.create_url, self.form_data, follow=True)
        doc = Document.objects.get(document_key='KEY')
        meta = doc.get_metadata()
        self.assertFalse(meta.status_std_actual_date)

        rev = meta.latest_revision
        self.assertFalse(rev.status)

        self.form_data.update({'status': 'STD'})
        self.client.post(doc.get_edit_url(), self.form_data, follow=True)

        rev.refresh_from_db()
        self.assertEqual(rev.status, 'STD')

        meta.refresh_from_db()
        self.assertEqual(meta.status_std_actual_date, self.today)

    def test_edit_revision_with_another_status(self):
        self.form_data.update({'status': 'STD'})
        self.client.post(self.create_url, self.form_data, follow=True)

        doc = Document.objects.get(document_key='KEY')
        self.form_data.update({'status': 'IFA'})
        self.client.post(doc.get_edit_url(), self.form_data, follow=True)

        meta = doc.get_metadata()
        self.assertEqual(meta.status_ifa_actual_date, self.today)
        self.assertIsNone(meta.status_std_actual_date, self.today)

        rev = meta.latest_revision
        self.assertEqual(rev.status, 'IFA')

    def test_create_revision_with_empty_status(self):
        self.form_data.update({'status': 'STD'})
        self.client.post(self.create_url, self.form_data, follow=True)
        doc = Document.objects.get(document_key='KEY')

        self.form_data.update({'status': ''})
        self.client.post(doc.get_revise_url(), self.form_data, follow=True)

        meta = doc.get_metadata()
        self.assertEqual(meta.status_std_actual_date, self.today)

        rev = meta.latest_revision
        self.assertEqual(rev.status, '')

    def test_create_revision_with_old_status_doesnt_update_date(self):
        five_days_ago = self.today - datetime.timedelta(days=5)

        self.form_data.update({
            'status': 'STD',
            'created_on': five_days_ago.strftime('%Y-%m-%d'),
            'received_date': five_days_ago.strftime('%Y-%m-%d'),
        })
        self.client.post(self.create_url, self.form_data, follow=True)

        doc = Document.objects.get(document_key='KEY')
        meta = doc.get_metadata()
        self.assertEqual(meta.status_std_actual_date, five_days_ago)

        self.client.post(doc.get_revise_url(), self.form_data, follow=True)
        meta.refresh_from_db()
        self.assertEqual(meta.status_std_actual_date, five_days_ago)

        rev = meta.latest_revision
        self.assertEqual(rev.status, 'STD')

    def test_edit_previous_revision(self):
        five_days_ago = self.today - datetime.timedelta(days=5)
        first_revision_data = self.form_data.copy()
        first_revision_data.update({
            'status': 'STD',
            'created_on': five_days_ago.strftime('%Y-%m-%d'),
            'received_date': five_days_ago.strftime('%Y-%m-%d'),
        })
        self.client.post(self.create_url, first_revision_data, follow=True)
        doc = Document.objects.get(document_key='KEY')
        meta = doc.get_metadata()

        self.form_data.update({'status': 'STD'})
        self.client.post(doc.get_revise_url(), self.form_data, follow=True)

        first_revision_data.update({'status': 'IFA'})
        self.client.post(doc.get_edit_url(revision=0), first_revision_data, follow=True)

        meta.refresh_from_db()
        self.assertEqual(meta.status_std_actual_date, self.today)

        first_revision_data.update({'status': 'STD'})
        self.client.post(doc.get_edit_url(revision=0), first_revision_data, follow=True)

        meta.refresh_from_db()
        self.assertEqual(meta.status_std_actual_date, five_days_ago)
