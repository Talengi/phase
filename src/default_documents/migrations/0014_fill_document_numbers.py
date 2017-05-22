# -*- coding: utf-8 -*-


from django.db import migrations
from documents.utils import get_all_document_classes
from django.db.models import F


def fill_document_numbers(apps, schema_editor):
    classes = get_all_document_classes()
    for _class in classes:
        _class.objects.update(document_number=F('document_key'))


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0013_auto_20151210_1121'),
    ]

    operations = [
        migrations.RunPython(fill_document_numbers)
    ]
