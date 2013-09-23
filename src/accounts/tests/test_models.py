from django.test import TestCase
from django.core import mail

from accounts.factories import UserFactory


class ActivationMailTests(TestCase):
    def setUp(self):
        self.user = UserFactory(name='Mail User')

    def test_email_is_sent(self):
        self.user.send_account_activation_email('token')
        self.assertEqual(len(mail.outbox), 1)

    def test_email_subject_contains_username(self):
        self.user.send_account_activation_email('token')
        self.assertTrue(mail.outbox[0].subject.endswith('Mail User'))

    def test_email_contains_token(self):
        self.user.send_account_activation_email('random123token')
        self.assertTrue('random123token' in mail.outbox[0].body)
