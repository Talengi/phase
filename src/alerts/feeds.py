# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, time

from django.contrib.syndication.views import Feed
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from documents.models import Document
from categories.views import CategoryMixin


class BaseAlertFeed(CategoryMixin, Feed):
    def populate(self, request, *args, **kwargs):
        self.request = request
        self.kwargs = kwargs
        self.extract_category()

    def __call__(self, request, *args, **kwargs):
        self.populate(request, *args, **kwargs)
        return super(FeedNewDocuments, self).__call__(request, *args, **kwargs)


# TODO Missing auth
class FeedNewDocuments(BaseAlertFeed):
    title = _('Latest documents')
    link = '/alerts/'
    description = _('List of newly created documents in the category')

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
