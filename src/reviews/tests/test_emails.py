# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime

from django.test import TestCase
from django.core import mail
from django.core.management import call_command
from django.utils import timezone

from categories.factories import CategoryFactory
from documents.factories import DocumentFactory
from default_documents.tests.test import ContractorDeliverableTestCase
from accounts.factories import UserFactory, EntityFactory
from reviews.models import Review


class PendingReviewsReminderTests(TestCase):
    def setUp(self):
        self.category = CategoryFactory()
        self.user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category
        )
        self.client.login(email=self.user.email, password='pass')
        self.doc1 = DocumentFactory(
            category=self.category,
            revision={
                'leader': self.user,
                'received_date': datetime.date.today(),
            }
        )
        self.doc2 = DocumentFactory(
            category=self.category,
            revision={
                'leader': self.user,
                'received_date': datetime.date.today(),
            }
        )

    def test_empty_reminder_list(self):
        call_command('send_review_reminders')
        self.assertEqual(len(mail.outbox), 0)

    def test_send_reminders(self):
        self.doc1.get_latest_revision().start_review()
        self.assertEqual(Review.objects.all().count(), 1)

        call_command('send_review_reminders')
        self.assertEqual(len(mail.outbox), 1)

    def test_finished_reviews(self):
        rev = self.doc1.get_latest_revision()
        rev.start_review()
        rev.end_review()
        self.assertEqual(Review.objects.all().count(), 1)

        call_command('send_review_reminders')
        self.assertEqual(len(mail.outbox), 0)

    def test_do_not_send_reminder(self):
        """Reminders are not send to users if their mail config says so."""
        self.doc1.get_latest_revision().start_review()
        self.assertEqual(Review.objects.all().count(), 1)

        self.user.send_pending_reviews_mails = False
        self.user.save()

        call_command('send_review_reminders')
        self.assertEqual(len(mail.outbox), 0)


class ClosedReviewsEmailTests(ContractorDeliverableTestCase):
    def setUp(self):
        super(ClosedReviewsEmailTests, self).setUp()
        self.today = timezone.now()
        self.yesterday = timezone.now() - datetime.timedelta(days=1)
        self.originator = EntityFactory(
            type='originator',
            users=[
                UserFactory(),
                UserFactory(),
                UserFactory(),
                UserFactory(send_closed_reviews_mails=False),
            ]
        )

    def test_end_review_today(self):
        data = {
            'revision': {
                'leader': self.user,
            }
        }
        doc = self.create_doc(**data)
        rev = doc.get_latest_revision()
        rev.start_review(at_date=self.today)
        rev.end_review(at_date=self.today)

        self.assertEqual(len(mail.outbox), 0)
        call_command('send_closed_reviews_notifications')
        self.assertEqual(len(mail.outbox), 0)

    def test_send_email_to_empty_originator(self):
        data = {
            'revision': {
                'leader': self.user,
            }
        }
        doc = self.create_doc(**data)
        rev = doc.get_latest_revision()
        rev.start_review(at_date=self.yesterday)
        rev.end_review(at_date=self.yesterday)

        self.assertEqual(len(mail.outbox), 0)
        call_command('send_closed_reviews_notifications')
        self.assertEqual(len(mail.outbox), 0)

    def test_send_email_to_originator_with_recipients(self):
        data = {
            'metadata': {
                'originator': self.originator,
            },
            'revision': {
                'leader': self.user,
            }
        }
        doc = self.create_doc(**data)
        rev = doc.get_latest_revision()
        rev.start_review(at_date=self.yesterday)
        rev.end_review(at_date=self.yesterday)

        self.assertEqual(len(mail.outbox), 0)
        call_command('send_closed_reviews_notifications')
        self.assertEqual(len(mail.outbox), 1)
        # We have 4 potential recipients but one has `
        # `send_closed_reviews_mails set to False
        self.assertEqual(len(mail.outbox[0].to), 3)
