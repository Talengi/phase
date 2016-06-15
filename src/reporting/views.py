# -*- coding: utf-8 -*-

import datetime
import json
from collections import Counter

from braces.views import LoginRequiredMixin
from django.core.exceptions import FieldError
from django.db.models import Func, Count, Q
from django.http import Http404
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

    See: http://stackoverflow.com/questions/35368274/django-count-grouping-by-year-month-without-extra
    """

    function = 'EXTRACT'
    template = '%(function)s(%(what_to_extract)s FROM %(expressions)s)'


def format_results(by_ended_reviews):
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
    for month in range(months):
        if curr_date.month == 12:
            curr_date = datetime.date(month=1, year=curr_date.year + 1,
                                      day=1)
        else:
            curr_date = datetime.date(month=curr_date.month + 1,
                                      year=curr_date.year, day=1)
        # If date does not exist, we fill with a 0
        if not any(curr_date in d.values() for d in by_ended_reviews):
            by_ended_reviews.append({'date': curr_date, 'value': 0})
    # Sorting again for client side processing
    by_ended_reviews = sorted(by_ended_reviews, key=lambda el: el['date'])
    # Formatting for js date instanciation
    by_ended_reviews = [
        {'month': el['date'].month, 'year': el['date'].year,
         'value': el['value']} for el in by_ended_reviews]

    return by_ended_reviews


class Report(LoginRequiredMixin, CategoryMixin, TemplateView):
    template_name = 'reporting/reports.html'

    def get(self, request, *args, **kwargs):
        if not self.category.category_template.display_reporting:
            raise Http404
        return super(Report, self).get(request, *args, **kwargs)

    @staticmethod
    def build_list(values):
        val_list = [{'value': (lambda x: x or 'None')(k), 'count': v} for k, v
                    in sorted(values.items())]
        return val_list

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
        return format_results(docs_by_month)

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
        try:
            docs_by_ended_reviews = self.get_revisions().exclude(
                review_end_date__isnull=True).annotate(
                year=Extract('review_end_date', what_to_extract='year'),
                month=Extract('review_end_date', what_to_extract='month')
            ).values('year', 'month').annotate(Count('pk'))
        except FieldError:
            return []
        return format_results(docs_by_ended_reviews)

    def get_docs_by_rc(self):
        try:
            docs_by_rc = self.get_documents().values_list(
                'latest_revision__return_code', flat=True)

        except FieldError:
            return []
        by_rc = Counter(docs_by_rc)
        return self.build_list(by_rc)

    def _filter_docs_by_reviews(self, filter_dict):
        """This generic method is called by concrete ones below."""
        users = self.category.users.all()
        docs = []

        try:
            revisions = self.get_revisions().filter(**filter_dict)
        except FieldError:
            return docs

        for user in users:
            revs = revisions.filter(
                Q(reviewers=user) |
                Q(leader=user) |
                Q(approver=user))
            count = revs.count()
            if count:
                docs.append({'value': user.name, 'count': count})
        return docs

    def get_docs_under_reviews(self):
        """Returns docs under review by user."""
        return self._filter_docs_by_reviews({
            'review_start_date__isnull': False,
            'review_end_date__isnull': True})

    def get_docs_with_overdue_review(self):
        """Returns docs under review which date is overdue by user."""
        today = datetime.datetime.today()
        return self._filter_docs_by_reviews({
            'review_start_date__isnull': False,
            'review_end_date__isnull': False,
            'review_due_date__lt': today})

    def get_context_data(self, **kwargs):
        ctx = super(Report, self).get_context_data(**kwargs)

        by_month = self.get_docs_by_month()

        by_status = self.get_docs_by_status()

        by_revs = self.get_docs_by_revs()
        by_rc = self.get_docs_by_rc()

        by_ended_reviews = self.get_docs_by_ended_reviews()

        under_review = self.get_docs_under_reviews()

        overdue_review = self.get_docs_with_overdue_review()
        ctx.update({'reporting_active': True,
                    'by_month': json.dumps(by_month),
                    'by_revs': json.dumps(by_revs),
                    'by_status': json.dumps(by_status),
                    'by_rc': json.dumps(by_rc),
                    'under_review': json.dumps(under_review),
                    'by_ended_reviews': json.dumps(by_ended_reviews),
                    'overdue_review': json.dumps(overdue_review)})
        return ctx
