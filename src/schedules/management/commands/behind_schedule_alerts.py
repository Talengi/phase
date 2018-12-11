import operator
from functools import reduce

from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.db.models import Q
from django.utils import timezone

from metadata.fields import get_choices_from_list
from schedules.models import ScheduleMixin
from categories.models import Category


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # Get all categories
        # Filter categories, get the ones with Metadata inheriting "ScheduleMixin"
        # For each category, fetch documents behind schedule

        categories = self.fetch_categories_with_schedulable_content()
        for category in categories:
            documents = self.fetch_documents_behind_schedule(category)
            print(list(documents))

    def fetch_categories_with_schedulable_content(self):
        """Fetch all categories where the document class has a Schedulable behavior."""

        categories = Category.objects \
            .select_related('category_template__metadata_model')

        def has_schedulable_content(category):
            metadata_cls = category.document_class()
            return issubclass(metadata_cls, ScheduleMixin)

        schedulables_categories = filter(has_schedulable_content, categories)
        return schedulables_categories

    def fetch_documents_behind_schedule(self, category):
        """Fetch documents behind schedule.

        Documents behind schedule are documents that were meant to reach a
        certain status at a certain date (forecast), and that date has
        already passed whereas the document still has not reached that status.

        It technical terms, it means:

          - in it's "schedule" table, the document has one line with a
            `forecast` value that is < today and an `actual` value that is null.
          - that lines concerns a status that is higher than the current status
            in the document workflow.
        """

        # Get the list of existing statuses for this category's document class
        Metadata = category.document_class()
        Revision = Metadata.get_revision_class()
        list_index = Revision._meta.get_field('status').list_index
        statuses = [
            status.lower() for status, _ in get_choices_from_list(list_index)
        ]
        today = timezone.now().date()

        # Create a first coarse filter to get all documents that MAY be
        # behind schedule.
        # Get all documents with any X status with a past forecast date AND
        # not actual date.
        #
        # However, that does not mean that this document is behind schedule,
        # because statuses can be skipped. E.g a document with a forecast date
        # for status A that goes directly to the next status B will have an
        # empty value for the `status_A_actual_date` but is still not
        # behind schedule.
        #
        # The reason we don't filter everything in a single query is because it
        # would make the said query ridiculously complex.
        conditions = []
        for status in statuses:
            forecast_field = 'status_{}_forecast_date__lt'.format(status)
            actual_field = 'status_{}_actual_date__isnull'.format(status)
            conditions.append(
                Q(**{forecast_field: today}) & Q(**{actual_field: True}))

        coarse_filter = reduce(operator.or_, conditions)
        documents = Metadata.objects \
            .filter(document__category=category) \
            .filter(coarse_filter)

        def is_behind_schedule(document):
            """Tells if a single document is actually behind schedule.

            Check for a "behind schedule" condition, but only for statuses
            that the document has not reached yet.
            """

            current_status = document.status.lower()
            # statuses are sorted by chronological order
            current_status_index = statuses.index(current_status)
            for status_index, status in enumerate(statuses):
                if status_index <= current_status_index:
                    # The document has already passed this status, ignore
                    # this schedule line.
                    continue

                forecast_field = 'status_{}_forecast_date'.format(status)
                actual_field = 'status_{}_actual_date'.format(status)

                if not hasattr(document, forecast_field):
                    continue

                forecast_date = getattr(document, forecast_field)
                actual_date = getattr(document, actual_field)
                if forecast_date < today and actual_date is None:
                    return True

            return False

        # Here, we filter the queryset to remove false positives.
        behind_schedule_documents = filter(is_behind_schedule, documents)
        return behind_schedule_documents
