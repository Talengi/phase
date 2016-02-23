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

        reviewed_docs = []
        yesterday = timezone.now().date() - timedelta(days=1)
        classes = get_all_reviewable_classes()
        for _class in classes:
            docs = _class.objects.filter(review_end_date=yesterday)
            reviewed_docs += list(docs)

        originators = groupby(reviewed_docs, lambda doc: doc.originator)
        for originator, docs in originators:
            print originator, docs

    def get_subject(self, **kwargs):
        return 'Phase - Pending reviews'

    def get_recipient_list(self, **kwargs):
        return [kwargs['user'].email]
