# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0008_auto_20151106_1014'),
    ]

    operations = [
        migrations.AlterField(
            model_name='outgoingtransmittal',
            name='related_documents',
            field=models.ManyToManyField(related_name='outgoing_transmittal_set', through='transmittals.ExportedRevision', to='documents.Document', blank=True),
        ),
    ]
