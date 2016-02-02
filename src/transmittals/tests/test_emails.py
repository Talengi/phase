# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.core import mail

from accounts.factories import UserFactory
from transmittals.factories import create_transmittal
from transmittals.utils import send_transmittal_creation_notifications


class TransmittalNotificationTests(TestCase):
    def setUp(self):
        pass

    def test_empty_notification_list(self):
        trs = create_transmittal()
        rev = trs.latest_revision
        send_transmittal_creation_notifications(trs, rev)

        self.assertEqual(len(mail.outbox), 0)

    def test_notification_list(self):
        trs = create_transmittal()
        rev = trs.latest_revision

        trs.recipient.users.add(UserFactory(email='riri@duck.com'))
        trs.recipient.users.add(UserFactory(email='fifi@duck.com'))
        trs.recipient.users.add(UserFactory(email='loulou@duck.com'))

        send_transmittal_creation_notifications(trs, rev)
        self.assertEqual(len(mail.outbox), 3)
