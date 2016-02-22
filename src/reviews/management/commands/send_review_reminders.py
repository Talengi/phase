#!/usr/bin/python
# -*- coding: utf-8 -*-

from itertools import groupby

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.template.loader import get_template
from django.contrib.sites.models import Site
from django.utils import translation
from django.conf import settings

from reviews.models import Review

BODY_TEMPLATE = 'reviews/pending_reviews_reminder_email.txt'
HTML_BODY_TEMPLATE = 'reviews/pending_reviews_reminder_email.html'


class Command(BaseCommand):
    help = 'Send an email reminder to all users with pending reviews'

    def handle(self, *args, **options):

        if not settings.SEND_EMAIL_REMINDERS:
            return

        translation.activate(settings.LANGUAGE_CODE)

        self.body_template = get_template(BODY_TEMPLATE)
        self.html_body_template = get_template(HTML_BODY_TEMPLATE)
        self.site = Site.objects.get_current()

        pending_reviews = Review.objects \
            .filter(status='progress') \
            .select_related('document', 'reviewer') \
            .order_by('reviewer', 'role')
        users = groupby(pending_reviews, lambda rev: rev.reviewer)
        for user, reviews in users:
            self.remind_user_of_pending_reviews(user, list(reviews))

    def remind_user_of_pending_reviews(self, user, reviews):
        """Send the reminder email."""
        import pdb; pdb.set_trace()
        send_mail(
            self.get_subject(user, reviews),
            self.get_body(user, reviews),
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=self.get_html_body(user, reviews),
            fail_silently=False)

    def get_subject(self, user, reviews):
        return 'Phase - Pending reviews'

    def get_body(self, user, reviews):
        return self.body_template.render({
            'user': user,
            'reviews': reviews,
            'site': self.site,
        })

    def get_html_body(self, user, reviews):
        return self.html_body_template.render({
            'user': user,
            'reviews': reviews,
            'site': self.site,
        })
