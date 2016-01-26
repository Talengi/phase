#!/usr/bin/python
# -*- coding: utf-8 -*-

from itertools import groupby

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.template.loader import get_template
from django.contrib.sites.models import Site
from django.conf import settings

from reviews.models import Review

BODY_TEMPLATE = 'reviews/pending_reviews_reminder_email.txt'


class Command(BaseCommand):
    help = 'Send an email reminder to all users with pending reviews'

    def handle(self, *args, **options):
        self.body_template = get_template(BODY_TEMPLATE)
        self.site = Site.objects.get_current()

        pending_reviews = Review.objects \
            .filter(status='pending') \
            .select_related('document', 'reviewer') \
            .order_by('reviewer')
        users = groupby(pending_reviews, lambda rev: rev.reviewer)
        for user, reviews in users:
            self.remind_user_of_pending_reviews(user, reviews)

    def remind_user_of_pending_reviews(self, user, reviews):
        """Send the reminder email."""
        send_mail(
            self.get_subject(user, reviews),
            self.get_body(user, reviews),
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False)

    def get_subject(self, user, reviews):
        return 'Phase - Document Reviews'

    def get_body(self, user, reviews):
        return self.body_template.render({
            'user': user,
            'reviews': reviews,
            'site': self.site,
        })
