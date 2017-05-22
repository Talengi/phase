# -*- coding: utf-8 -*-


from django.conf import settings

from core.celery import app

from accounts.models import User
from audit_trail.models import Activity
from audit_trail.signals import activity_log


@app.task
def process_export(export_id, user_pk=None):
    from exports.models import Export
    export = Export.objects.select_related().get(id=export_id)

    # Cleanup oldest export when there are too many
    owner = export.owner
    oldest_exports_qs = Export.objects \
        .filter(owner=owner) \
        .order_by('-created_on') \
        .all()
    oldest_exports = list(oldest_exports_qs)
    if len(oldest_exports) > settings.EXPORTS_TO_KEEP:
        oldest_export_index = settings.EXPORTS_TO_KEEP - 1
        oldest_export = oldest_exports[oldest_export_index]
        Export.objects \
            .filter(owner=owner) \
            .filter(created_on__lt=oldest_export.created_on) \
            .delete()
    user = User.objects.get(pk=user_pk)
    export.status = 'processing'
    export.save()
    export.write_file()
    export.status = 'done'
    export.save()
    activity_log.send(verb=Activity.VERB_CREATED,
                      action_object_str=export.get_pretty_filename(),
                      sender=None,
                      actor=user)
