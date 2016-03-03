#!/usr/bin/python
# -*- coding: utf-8 -*-

from itertools import groupby

from notifications.management.commands.base import EmailCommand
from reviews.models import Review


class Command(EmailCommand):
    help = 'Send an email reminder to all users with pending reviews'
    text_template = 'reviews/pending_reviews_reminder_email.txt'
    html_template = 'reviews/pending_reviews_reminder_email.html'

    def handle(self, *args, **options):
        pending_reviews = Review.objects \
            .filter(status='progress') \
            .select_related('document', 'reviewer') \
            .order_by('reviewer', 'role')
        users = groupby(pending_reviews, lambda rev: rev.reviewer)
        for user, reviews in users:
            if not user.send_pending_reviews_mails:
                continue
            self.send_notification(user=user, reviews=list(reviews))

    def get_subject(self, **kwargs):
        return 'Phase - Pending reviews'

    def get_recipient_list(self, **kwargs):
        return [kwargs['user'].email]
