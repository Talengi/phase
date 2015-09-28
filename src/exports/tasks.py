# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from core.celery import app
from notifications.models import notify


@app.task
def process_export(export_id):
    from exports.models import Export
    export = Export.objects.select_related().get(id=export_id)
    export.status = 'processing'
    export.save()
    export.write_file()
    export.status = 'done'
    export.save()

    url = export.get_absolute_url()
    message = _('The export <a href="{}">you required for category {} is ready</a>.'.format(
        url, export.category))
    notify(export.owner, message)
