# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.views.generic import TemplateView, ListView
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured

from braces.views import LoginRequiredMixin

from categories.views import CategoryMixin
from feeds import feeds


class AlertHome(LoginRequiredMixin, CategoryMixin, TemplateView):
    """Simply links to available feeds."""
    template_name = 'feeds/alert_home.html'

    def breadcrumb_section(self):
        return (_('Feeds'), '#')

    def breadcrumb_subsection(self):
        return self.category


class FeedConverterMixin(object):
    """Displays a Django Feed directly in html."""
    feed_class = None

    def dispatch(self, request, *args, **kwargs):
        self.extract_feed()
        return super(FeedConverterMixin, self).dispatch(request, *args, **kwargs)

    def extract_feed(self):
        """Get the feed to display."""
        if self.feed_class is None:
            raise ImproperlyConfigured('Missing `feed` field')

        feed = self.feed_class()
        feed.populate(self.request, **self.kwargs)
        self.category = feed.category
        feed_object = feed.get_object(self.request, *self.args, **self.kwargs)
        rss_feed = feed.get_feed(feed_object, self.request)
        self.feed = rss_feed


class BaseAlert(LoginRequiredMixin,
                FeedConverterMixin,
                ListView):

    template_name = 'feeds/alert_list.html'
    context_object_name = 'alerts'

    def breadcrumb_section(self):
        return (_('Feeds'), '#')

    def breadcrumb_subsection(self):
        return (self.category, reverse('category_feeds', args=[
            self.category.organisation.slug,
            self.category.slug
        ]))

    def get_queryset(self):
        items = self.feed.items
        return items

    def get_context_data(self, **kwargs):
        context = super(BaseAlert, self).get_context_data(**kwargs)
        context.update({
            'title': self.feed.feed['title'],
            'description': self.feed.feed['description'],
            'feed_url': self.feed.feed['link'],
        })
        return context


class AlertNewDocuments(BaseAlert):
    """List newly created documents."""
    feed_class = feeds.FeedNewDocuments

    def breadcrumb_object(self):
        return (_('New documents'), reverse('alert_new_documents', args=[
            self.category.organisation.slug,
            self.category.slug
        ]))


class AlertClosedReviews(BaseAlert):
    """List newly closed reviews."""
    feed_class = feeds.FeedClosedReviews

    def breadcrumb_object(self):
        return (_('Closed reviews'), reverse('alert_closed_reviews', args=[
            self.category.organisation.slug,
            self.category.slug
        ]))


class AlertStartedReviews(BaseAlert):
    """List newly created reviews."""
    feed_class = feeds.FeedStartedReviews

    def breadcrumb_object(self):
        return (_('Started reviews'), reverse('alert_started_reviews', args=[
            self.category.organisation.slug,
            self.category.slug
        ]))


class AlertOverdueDocuments(BaseAlert):
    """List overdue documents."""
    feed_class = feeds.FeedOverdueDocuments

    def breadcrumb_object(self):
        return (_('Overdue documents'), reverse('alert_overdue_documents', args=[
            self.category.organisation.slug,
            self.category.slug
        ]))
