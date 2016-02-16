#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from datetime import timedelta

from itertools import groupby

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.template.loader import get_template
from django.contrib.sites.models import Site
from django.utils import translation, timezone
from django.conf import settings

from transmittals.models import OutgoingTransmittal

BODY_TEMPLATE = 'transmittals/pending_ack_email.txt'
HTML_BODY_TEMPLATE = 'transmittals/pending_ack_email.html'


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send reminders for trs with missing ack of receipt.'

    def handle(self, *args, **options):

        if not settings.SEND_EMAIL_REMINDERS:
            return

        logger.info('Sending transmittal reminders')

        translation.activate(settings.LANGUAGE_CODE)

        self.body_template = get_template(BODY_TEMPLATE)
        self.html_body_template = get_template(HTML_BODY_TEMPLATE)
        self.site = Site.objects.get_current()

        delta = timezone.now().date() - timedelta(days=1)
        transmittals = OutgoingTransmittal.objects \
            .filter(ack_of_receipt_date__isnull=True) \
            .filter(document__created_on__lt=delta) \
            .select_related() \
            .prefetch_related('recipient__users')

        recipients = groupby(transmittals, lambda trs: trs.recipient)
        for recipient, transmittals in recipients:
            self.send_reminder(recipient, list(transmittals))

    def send_reminder(self, recipient, transmittals):
        """Send the reminder email."""
        logger.info('Sending reminders for recipient {}'.format(recipient.name))

        for user in recipient.users.all():
            send_mail(
                self.get_subject(user, transmittals),
                self.get_body(user, transmittals),
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=self.get_html_body(user, transmittals),
                fail_silently=False)

    def get_subject(self, user, transmittals):
        return 'Phase - Transmittals pending acknowledgment of receipt'

    def get_body(self, user, transmittals):
        return self.body_template.render({
            'user': user,
            'transmittals': transmittals,
            'site': self.site,
        })

    def get_html_body(self, user, transmittals):
        return self.html_body_template.render({
            'user': user,
            'transmittals': transmittals,
            'site': self.site,
        })
