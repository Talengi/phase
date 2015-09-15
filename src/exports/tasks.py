# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from core.celery import app


@app.task
def process_export(export_id):
    from exports.models import Export
    export = Export.objects.get(id=export_id)
    export.write_file()
    export.status = 'done'
    export.save
