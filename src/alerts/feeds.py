# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
from datetime import datetime, time

from django.contrib.syndication.views import Feed
from django.views.generic import View
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.utils import timezone
from django.template.loader import render_to_string
from django.conf import settings

from documents.models import Document
from categories.views import CategoryMixin


class HttpResponseUnauthorized(HttpResponse):
    status_code = 401

    def __init__(self, *args, **kwargs):
        super(HttpResponseUnauthorized, self).__init__(*args, **kwargs)
        self['WWW-Authenticate'] = 'Basic realm="Phase feeds"'


class AlertMixin(object):
    """Base class for all alert rss feeds.

    Since those views are made to be fetched by feed readers, we need to
    handle authentication differently here.

    Most readers only accept basic http authentication. We need to make sure
    that the request is secure (e.g uses ssl) before asking for non-encrypted
    login + password.

    """
    def authenticate_user(self, request):
        try:
            auth = request.META['HTTP_AUTHORIZATION'].split()
            decoded_auth = base64.b64decode(auth[1])
            username, password = decoded_auth.split(':')
        except:
            # Invalid authorization header sent by client
            # Let's block everything.
            raise PermissionDenied()

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)

    def dispatch(self, request, *args, **kwargs):
        if 'HTTP_AUTHORIZATION' in request.META:
            self.authenticate_user(request)

        if not self.request.user.is_authenticated():
            if self.request.is_secure():
                return HttpResponseUnauthorized('Unauthorized')
            else:
                msg = _('This url cannot be accessed through a non-secure protocol')
                raise PermissionDenied(msg)
        else:
            return super(AlertMixin, self).dispatch(request, *args, **kwargs)


class BaseAlertFeed(AlertMixin, Feed, View):
    def get(self, request, *args, **kwargs):
        # Feed.__call__(…)
        return self(request, *args, **kwargs)


class BaseCategoryAlertFeed(AlertMixin, CategoryMixin, Feed, View):
    """Base class for alerts in a single category."""
    def populate(self, request, *args, **kwargs):
        self.request = request
        self.kwargs = kwargs
        self.extract_category()

    def get(self, request, *args, **kwargs):
        self.populate(request, *args, **kwargs)
        # Feed.__call__(…)
        return self(request, *args, **kwargs)


class FeedNewDocuments(BaseCategoryAlertFeed):
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
        return render_to_string('alerts/revision_document.html', {'item': item})

    def item_pubdate(self, item):
        # Feeds expect a full datetime obj but documents only store
        # created date. Thus, we have to convert the value to an actual
        # datetime.
        return datetime.combine(item.created_on, time())


class FeedClosedReviews(BaseCategoryAlertFeed):
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
        return render_to_string('alerts/revision_item.html', {'item': item})

    def item_pubdate(self, item):
        # Feeds expect a full datetime obj but documents only store
        # created date. Thus, we have to convert the value to an actual
        # datetime.
        return datetime.combine(item.review_end_date, time())


class FeedStartedReviews(BaseCategoryAlertFeed):
    title = _('Documents under reviews')
    description = _('Documents that just went under review.')

    def link(self):
        return reverse('feed_started_reviews', args=[
            self.category.organisation.slug,
            self.category.slug
        ])

    def items(self, *args, **kwargs):
        qs = self.category.revision_class().objects \
            .filter(metadata__document__category=self.category) \
            .filter(review_start_date__isnull=False) \
            .select_related('metadata__document') \
            .order_by('-review_start_date')[:settings.ALERT_ELEMENTS]
        return qs

    def item_link(self, item):
        return item.metadata.document.get_absolute_url()

    def item_title(self, item):
        return item.metadata.title

    def item_description(self, item):
        return render_to_string('alerts/revision_item.html', {'item': item})

    def item_pubdate(self, item):
        # Feeds expect a full datetime obj but documents only store
        # created date. Thus, we have to convert the value to an actual
        # datetime.
        return datetime.combine(item.review_start_date, time())


class FeedOverdueDocuments(BaseCategoryAlertFeed):
    title = _('Overdue documents')
    description = _('Overdue documents.')

    def link(self):
        return reverse('feed_overdue_documents', args=[
            self.category.organisation.slug,
            self.category.slug
        ])

    def items(self, *args, **kwargs):
        today = timezone.now().date()
        qs = self.category.revision_class().objects \
            .filter(metadata__document__category=self.category) \
            .filter(review_start_date__isnull=False) \
            .filter(review_end_date__isnull=True) \
            .filter(review_due_date__lt=today) \
            .select_related('metadata__document') \
            .order_by('-review_due_date')[:settings.ALERT_ELEMENTS]
        return qs

    def item_link(self, item):
        return item.metadata.document.get_absolute_url()

    def item_title(self, item):
        return item.metadata.title

    def item_description(self, item):
        return render_to_string('alerts/revision_item.html', {'item': item})

    def item_pubdate(self, item):
        return datetime.combine(item.review_due_date, time())
