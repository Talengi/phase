# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.core.urlresolvers import reverse

from accounts.factories import UserFactory
from transmittals.factories import create_transmittal


ack_button = '<a id="action-ack-transmittal"'


class TransmittalActionTests(TestCase):

    def setUp(self):
        self.trs = create_transmittal()
        self.doc = self.trs.document
        self.category = self.doc.category
        self.url = reverse("document_detail", args=[
            self.category.organisation.slug,
            self.category.slug,
            self.doc.document_key
        ])
        self.user = UserFactory(
            name='User',
            password='pass',
            is_superuser=True,
            category=self.category)
        self.client.login(username=self.user.email, password='pass')

    def test_internal_user_cannot_ack_transmittal(self):
        self.assertIsNone(self.trs.ack_of_receipt_date)
        self.assertFalse(self.user.is_external)

        res = self.client.get(self.url)
        self.assertNotContains(res, ack_button)

    def test_external_user_can_ack_transmittal(self):
        self.user.is_external = True
        self.user.save()

        res = self.client.get(self.url)
        self.assertContains(res, ack_button)

    def test_transmittal_cannot_be_acked_twice(self):
        self.user.is_external = True
        self.trs.ack_receipt(self.user)

        self.assertIsNotNone(self.trs.ack_of_receipt_date)

        res = self.client.get(self.url)
        self.assertNotContains(res, ack_button)
