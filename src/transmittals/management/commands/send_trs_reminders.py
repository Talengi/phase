#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from datetime import timedelta

from itertools import groupby

from django.utils import timezone

from notifications.management.commands.base import EmailCommand
from transmittals.models import OutgoingTransmittal


logger = logging.getLogger(__name__)


class Command(EmailCommand):
    help = 'Send reminders for trs with missing ack of receipt.'
    text_template = 'transmittals/pending_ack_email.txt'
    html_template = 'transmittals/pending_ack_email.html'

    def handle(self, *args, **options):

        logger.info('Sending transmittal reminders')

        delta = timezone.now().date() - timedelta(days=1)
        transmittals = OutgoingTransmittal.objects \
            .filter(ack_of_receipt_date__isnull=True) \
            .filter(document__created_on__lt=delta) \
            .select_related() \
            .prefetch_related('recipient__users')

        recipients = groupby(transmittals, lambda trs: trs.recipient)
        for recipient, transmittals in recipients:
            logger.info('Sending reminders for recipient {}'.format(recipient.name))
            for user in recipient.users.all():
                self.send_notification(
                    user=user, transmittals=list(transmittals))

    def get_subject(self, **kwargs):
        return 'Phase - Transmittals pending acknowledgment of receipt'

    def get_recipient_list(self, **kwargs):
        return [kwargs['user'].email]
