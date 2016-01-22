# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from core.celery import app
from notifications.models import notify


@app.task
def process_export(export_id):
    from exports.models import Export
    export = Export.objects.select_related().get(id=export_id)

    # Cleanup oldest export when there are too many
    owner = export.owner
    oldest_export_index = settings.EXPORTS_TO_KEEP - 1
    oldest_export = Export.objects \
        .filter(owner=owner) \
        .order_by('-created_on') \
        .all()[oldest_export_index]
    Export.objects \
        .filter(owner=owner) \
        .filter(created_on__lt=oldest_export.created_on) \
        .delete()

    export.status = 'processing'
    export.save()
    export.write_file()
    export.status = 'done'
    export.save()

    url = export.get_absolute_url()
    message = _('The export <a href="{}">you required for category {} is ready</a>.'.format(
        url, export.category))
    notify(export.owner, message)
