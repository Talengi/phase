# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from metadata.fields import get_choices_from_list
from schedules.models import ScheduleMixin


def update_schedule_section(document, metadata, revision, **kwargs):
    """Update the "actual" dates of the schedule section.

    The "<status> Actual Date" fields must be updated automatically depending
    on the different revisions' statuses and created date.

    See #172

    """
    sender = kwargs.pop('sender')
    if not issubclass(sender, ScheduleMixin):
        return

    list_index = revision._meta.get_field('status').list_index
    statuses = get_choices_from_list(list_index)
    for status, _ in statuses:
        field = 'status_{}_actual_date'.format(status).lower()
        setattr(metadata, field, None)

    revisions = document.get_all_revisions()
    for rev in revisions.reverse():
        if rev.status:
            field = 'status_{}_actual_date'.format(rev.status).lower()
            if not getattr(metadata, field, None):
                setattr(metadata, field, rev.created_on)

    metadata.save()
