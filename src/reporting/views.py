# -*- coding: utf-8 -*-

import datetime
import json
from collections import Counter

from braces.views import LoginRequiredMixin
from django.db.models import Func, Count
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView

from categories.views import CategoryMixin


class Extract(Func):
    """
    Performs extraction of `what_to_extract` from `*expressions`.

    Arguments:
        *expressions (string): Only single value is supported, should be field name to
                               extract from.
        what_to_extract (string): Extraction specificator.

    Returns:
        class: Func() expression class, representing 'EXTRACT(`what_to_extract` FROM `*expressions`)'.
    """

    function = 'EXTRACT'
    template = '%(function)s(%(what_to_extract)s FROM %(expressions)s)'


def format_sth(by_ended_reviews):
    if not by_ended_reviews:
        return []

    def el_to_date(elt):
        return datetime.date(month=int(elt['month']),
                             year=int(elt['year']),
                             day=1)

    by_ended_reviews = map(
        lambda e: {'value': e['pk__count'], 'date': el_to_date(e)},
        by_ended_reviews)
    # We need to fill with 0
    by_ended_reviews = sorted(by_ended_reviews, key=lambda e: e['date'])
    first_dt = by_ended_reviews[0]['date']
    last_dt = by_ended_reviews[-1]['date']
    # How many month in date range
    months = (last_dt.year - first_dt.year) * 12 + \
             last_dt.month - first_dt.month
    # We iterate over months to fill missing values with 0
    curr_date = first_dt
    for month in xrange(months):
        if curr_date.month == 12:
            curr_date = datetime.date(month=1, year=curr_date.year + 1,
                                      day=1)
        else:
            curr_date = datetime.date(month=curr_date.month + 1,
                                      year=curr_date.year, day=1)
        # If date does not exist, we fill with a 0
        if not any(curr_date in d.values() for d in by_ended_reviews):
            by_ended_reviews.append({'date': curr_date, 'value': 0})
    # Sorting again fo client side processing
    by_ended_reviews = sorted(by_ended_reviews, key=lambda el: el['date'])
    # Formatting for js date instanciation
    by_ended_reviews = [
        {'month': el['date'].month, 'year': el['date'].year,
         'value': el['value']} for el in by_ended_reviews]

    return by_ended_reviews


class Report(LoginRequiredMixin, CategoryMixin, TemplateView):
    template_name = 'reporting/reports.html'

    @staticmethod
    def build_list(values):
        return [{'value': (lambda x: x or 'None')(k), 'count': v} for k, v in
                values.items()]

    def breadcrumb_section(self):
        return _('Reporting')

    def breadcrumb_subsection(self):
        return self.category

    def get_metadata_class(self):
        return self.category.document_class()

    def get_revision_class(self):
        return self.category.revision_class()

    def get_documents(self):
        docs = self.get_metadata_class().objects.filter(
            document__category=self.category,
            document__category__organisation=self.category.organisation)
        return docs

    def get_revisions(self):
        revs = self.get_revision_class().objects.filter(
            metadata__document__category=self.category,
            metadata__document__category__organisation=self.category.organisation)
        return revs

    def get_docs_by_status(self):
        """Count documents by status"""
        docs_by_status = self.get_documents().values_list(
            'latest_revision__status', flat=True)
        by_status = Counter(docs_by_status)
        return self.build_list(by_status)

    def get_docs_by_month(self):
        """Count documents received by month"""
        docs_by_month = self.get_revisions().annotate(
            year=Extract('received_date', what_to_extract='year'),
            month=Extract('received_date', what_to_extract='month')
        ).values('year', 'month').annotate(Count('pk'))
        return format_sth(docs_by_month)

    def get_docs_by_revs(self):
        """Count documents received by numbers of revs"""
        related_name = self.get_revision_class().__name__.lower()
        docs_by_revs = self.get_documents().annotate(
            nb_rev=Count(related_name)). \
            values_list('nb_rev', flat=True)
        by_revs = Counter(docs_by_revs)
        return self.build_list(by_revs)

    def get_docs_by_ended_reviews(self):
        """Count revisions ended in each month"""
        docs_by_ended_reviews = self.get_revisions().exclude(
            review_end_date__isnull=True).annotate(
            year=Extract('review_end_date', what_to_extract='year'),
            month=Extract('review_end_date', what_to_extract='month')
        ).values('year', 'month').annotate(Count('pk'))

        return format_sth(docs_by_ended_reviews)

    def get_docs_by_rc(self):
        docs_by_rc = self.get_documents().values_list(
            'latest_revision__return_code', flat=True)
        by_rc = Counter(docs_by_rc)
        return self.build_list(by_rc)

    def get(self, request, *args, **kwargs):
        return super(Report, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(Report, self).get_context_data(**kwargs)

        by_month = self.get_docs_by_month()

        by_status = self.get_docs_by_status()

        by_revs = self.get_docs_by_revs()
        by_rc = self.get_docs_by_rc()

        by_ended_reviews = self.get_docs_by_ended_reviews()

        ctx.update({'reporting_active': True,
                    'by_month': json.dumps(by_month),
                    'by_revs': json.dumps(by_revs),
                    'by_status': json.dumps(by_status),
                    'by_rc': json.dumps(by_rc),
                    'by_ended_reviews': json.dumps(by_ended_reviews)})
        return ctx
