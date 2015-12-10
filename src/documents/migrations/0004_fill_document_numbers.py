# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.db.models import F


def fill_document_numbers(apps, schema_editor):
    Document = apps.get_model('documents', 'Document')
    Document.objects.update(document_number=F('document_key'))


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0003_auto_20151210_1039'),
    ]

    operations = [
        migrations.RunPython(fill_document_numbers)
    ]
