# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from feeds.feeds import BaseAlertFeed
from reviews.views import (
    ReviewersDocumentList, LeaderDocumentList, ApproverDocumentList)


class BaseReviewFeed(BaseAlertFeed):
    def items(self, *args, **kwargs):
        return self.get_queryset()

    def item_title(self, item):
        return item.document.title

    def item_description(self, item):
        return ''

    def item_pubdate(self, item):
        return item.created_on

    def item_link(self, item):
        return reverse('review_document', args=[item.document.document_key])

    def get_queryset(self):
        qs = super(BaseReviewFeed, self).get_queryset()
        return qs.order_by('created_on')


class FeedReviewersDocumentList(BaseReviewFeed, ReviewersDocumentList):
    title = _("Documents for which I'm a reviewer")
    description = ''

    def link(self):
        return reverse('feed_reviewers_review_document_list')


class FeedLeaderDocumentList(BaseReviewFeed, LeaderDocumentList):
    title = _("Documents for which I'm review leader")
    description = ''

    def link(self):
        return reverse('feed_leader_review_document_list')


class FeedApproverDocumentList(BaseReviewFeed, ApproverDocumentList):
    title = _("Documents for which I'm a review approver")
    description = ''

    def link(self):
        return reverse('feed_approver_review_document_list')
