# -*- coding: utf-8 -*-

import datetime

from django.test import TestCase
from django.core import mail
from django.core.management import call_command
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from categories.factories import CategoryFactory
from accounts.factories import UserFactory
from metadata.handlers import populate_values_list_cache
from documents.factories import DocumentFactory
from default_documents.models import ContractorDeliverable
from default_documents.factories import (
    ContractorDeliverableFactory, ContractorDeliverableRevisionFactory)


today = timezone.now()
yesterday = today - datetime.timedelta(days=1)


class ScheduleAlertTests(TestCase):

    fixtures = ['initial_values_lists']

    def setUp(self):
        super().setUp()
        Model = ContentType.objects.get_for_model(ContractorDeliverable)
        self.cat1 = CategoryFactory(category_template__metadata_model=Model)
        self.cat2 = CategoryFactory(category_template__metadata_model=Model)

        self.user1 = UserFactory(
            email='user1@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.cat1,
            send_behind_schedule_alert_mails=True)
        self.user1.categories.add(self.cat2)
        self.user2 = UserFactory(
            email='user2@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.cat2,
            send_behind_schedule_alert_mails=True)

        self.doc1 = DocumentFactory(
            category=self.cat1,
            metadata_factory_class=ContractorDeliverableFactory,
            revision_factory_class=ContractorDeliverableRevisionFactory)
        self.doc2 = DocumentFactory(
            category=self.cat2,
            metadata_factory_class=ContractorDeliverableFactory,
            revision_factory_class=ContractorDeliverableRevisionFactory)

        populate_values_list_cache()

    def test_empty_notification_list(self):
        """No documents are behind schedule, no alerts must be sent."""

        call_command('behind_schedule_alerts')
        self.assertEqual(len(mail.outbox), 0)

    def test_no_alert_when_the_status_is_passed(self):
        """Only future statuses are taken into account."""

        metadata = self.doc2.metadata
        metadata.status_ifr_forecast_date = yesterday
        metadata.status_ifr_actual_date = None
        metadata.save()

        revision = metadata.latest_revision
        revision.status = 'IFA'
        revision.save()
        call_command('behind_schedule_alerts')
        self.assertEqual(len(mail.outbox), 0)


    def test_one_document_is_behind_schedule(self):
        """Doc2 is late, both users must receive an alert."""

        metadata = self.doc2.metadata
        metadata.status_ifr_forecast_date = yesterday
        metadata.status_ifr_actual_date = None
        metadata.save()

        revision = metadata.latest_revision
        revision.status = 'STD'
        revision.save()
        call_command('behind_schedule_alerts')
        self.assertEqual(len(mail.outbox), 2)

    def test_alert_takes_acl_into_acount(self):
        """Doc1 is late, only user1 receives an alert.

        That's because user2 does not have access to the category 1.
        """

        metadata = self.doc1.metadata
        metadata.status_ifr_forecast_date = yesterday
        metadata.status_ifr_actual_date = None
        metadata.save()

        revision = metadata.latest_revision
        revision.status = 'STD'
        revision.save()
        call_command('behind_schedule_alerts')
        self.assertEqual(len(mail.outbox), 1)
