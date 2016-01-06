# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from metadata.fields import get_choices_from_list


def cd_post_save(document, metadata, revision, **kwargs):
    """When CD is saved, update the schedule section."""
    statuses = get_choices_from_list('STATUSES')
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
