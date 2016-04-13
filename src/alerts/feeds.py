# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, time

from django.contrib.syndication.views import Feed
from django.views.generic import View
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.conf import settings

from braces.views import LoginRequiredMixin

from documents.models import Document
from categories.views import CategoryMixin


class BaseAlertFeed(LoginRequiredMixin, CategoryMixin, Feed, View):
    raise_exception = True

    def populate(self, request, *args, **kwargs):
        self.request = request
        self.kwargs = kwargs
        self.extract_category()

    def dispatch(self, request, *args, **kwargs):
        return super(BaseAlertFeed, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.populate(request, *args, **kwargs)
        return self(request, *args, **kwargs)


class FeedNewDocuments(BaseAlertFeed):
    title = _('Latest documents')
    description = _('List of newly created documents in the category')

    def link(self):
        return reverse('feed_new_documents', args=[
            self.category.organisation.slug,
            self.category.slug
        ])

    def items(self, *args, **kwargs):
        qs = Document.objects \
            .filter(category=self.category) \
            .order_by('-created_on')[:settings.ALERT_ELEMENTS]
        return qs

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return ''

    def item_pubdate(self, item):
        # Feeds expect a full datetime obj but documents only store
        # created date. Thus, we have to convert the value to an actual
        # datetime.
        return datetime.combine(item.created_on, time())


class FeedClosedReviews(BaseAlertFeed):
    title = _('Closed reviews')
    description = _('List of recently closed reviews')

    def link(self):
        return reverse('feed_closed_reviews', args=[
            self.category.organisation.slug,
            self.category.slug
        ])

    def items(self, *args, **kwargs):
        qs = self.category.revision_class().objects \
            .filter(metadata__document__category=self.category) \
            .filter(review_end_date__isnull=False) \
            .select_related('metadata__document') \
            .order_by('-review_end_date')[:settings.ALERT_ELEMENTS]
        return qs

    def item_link(self, item):
        return item.metadata.document.get_absolute_url()

    def item_title(self, item):
        return item.metadata.title

    def item_description(self, item):
        return 'Return code = {}'.format(item.return_code)

    def item_pubdate(self, item):
        # Feeds expect a full datetime obj but documents only store
        # created date. Thus, we have to convert the value to an actual
        # datetime.
        return datetime.combine(item.review_end_date, time())
