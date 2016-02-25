#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import timedelta
from itertools import groupby

from django.utils import timezone

from notifications.management.commands.base import EmailCommand
from reviews.utils import get_all_reviewable_classes


class Command(EmailCommand):
    help = 'Send an email with the list of reviews closed yesterday'
    text_template = 'reviews/closed_reviews_list_email.txt'
    html_template = 'reviews/closed_reviews_list_email.html'

    def handle(self, *args, **options):

        reviewed_revisions = []
        yesterday = timezone.now().date() - timedelta(days=1)
        classes = get_all_reviewable_classes()
        for class_ in classes:
            revs = class_.objects \
                .select_related() \
                .filter(review_end_date=yesterday)
            reviewed_revisions += list(revs)

        originators = groupby(reviewed_revisions, lambda rev: rev.metadata.originator)
        for originator, revs in originators:
            self.send_notification(originator=originator, revisions=list(revs))

    def get_subject(self, **kwargs):
        return 'Phase - Pending reviews'

    def get_recipient_list(self, **kwargs):
        return ['test@toto.com']
