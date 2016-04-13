# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import TemplateView, ListView
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured

from braces.views import LoginRequiredMixin

from categories.views import CategoryMixin
from alerts import feeds


class AlertHome(LoginRequiredMixin, CategoryMixin, TemplateView):
    """Simply links to available alerts."""
    template_name = 'alerts/alert_home.html'

    def breadcrumb_section(self):
        return (_('Alerts'), '#')

    def breadcrumb_subsection(self):
        return self.category


class FeedConverterMixin(object):
    """Displays a Django Feed directly in html."""
    feed_class = None

    def dispatch(self, request, *args, **kwargs):
        self.feed = self.get_feed()
        return super(FeedConverterMixin, self).dispatch(request, *args, **kwargs)

    def get_feed(self):
        """Get the feed to display."""
        if self.feed_class is None:
            raise ImproperlyConfigured('Missing `feed` field')

        feed = self.feed_class()
        feed.populate(self.request, **self.kwargs)
        feed_object = feed.get_object(self.request, *self.args, **self.kwargs)
        rss_feed = feed.get_feed(feed_object, self.request)
        return rss_feed


class BaseAlert(LoginRequiredMixin,
                FeedConverterMixin,
                CategoryMixin,
                ListView):

    template_name = 'alerts/alert_list.html'
    context_object_name = 'alerts'

    def breadcrumb_section(self):
        return (_('Alerts'), '#')

    def breadcrumb_subsection(self):
        return (self.category, reverse('alert_home', args=[
            self.category.organisation.slug,
            self.category.slug
        ]))

    def get_queryset(self):
        items = self.get_feed().items
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
