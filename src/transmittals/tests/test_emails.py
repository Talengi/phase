# -*- coding: utf-8 -*-


from datetime import timedelta

from django.test import TestCase
from django.core import mail
from django.core.management import call_command
from django.utils import timezone

from accounts.factories import UserFactory
from transmittals.factories import create_transmittal
from transmittals.utils import send_transmittal_creation_notifications


class TransmittalNotificationTests(TestCase):
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


class TransmittalReminderTests(TestCase):
    def setUp(self):
        self.trs = create_transmittal()
        self.trs.recipient.users.add(UserFactory(email='riri@duck.com'))
        self.trs.recipient.users.add(UserFactory(email='fifi@duck.com'))
        self.trs.recipient.users.add(UserFactory(email='loulou@duck.com'))
        self.trs.recipient.users.add(UserFactory(
            email='scrooge@duck.com',
            send_trs_reminders_mails=False))

    def test_send_reminder_before_timer(self):
        call_command('send_trs_reminders')
        self.assertEqual(len(mail.outbox), 0)

    def test_send_reminders(self):
        two_days_ago = timezone.now().date() - timedelta(days=2)
        self.trs.document.created_on = two_days_ago
        self.trs.document.save()

        call_command('send_trs_reminders')
        self.assertEqual(len(mail.outbox), 3)

    def test_send_reminders_when_already_acked(self):
        two_days_ago = timezone.now().date() - timedelta(days=2)
        self.trs.document.created_on = two_days_ago
        self.trs.document.save()
        self.trs.ack_receipt(UserFactory())

        call_command('send_trs_reminders')
        self.assertEqual(len(mail.outbox), 0)
