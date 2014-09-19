from core.celery import app
from imports.models import ImportBatch


@app.task
def do_import(batch_uid):
    batch = ImportBatch.objects.get(uid=batch_uid)
    batch.do_import()
