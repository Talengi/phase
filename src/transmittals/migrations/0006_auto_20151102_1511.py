# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import transmittals.fields


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0005_auto_20151102_1441'),
    ]

    operations = [
        migrations.AlterField(
            model_name='outgoingtransmittal',
            name='related_documents',
            field=transmittals.fields.ManyDocumentsField(related_name='outgoing_transmittal_set', through='transmittals.ExportedRevision', to='documents.Document', blank=True),
        ),
    ]
