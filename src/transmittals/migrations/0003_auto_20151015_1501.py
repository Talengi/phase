# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0002_auto_20150812_1036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transmittal',
            name='accepted_dir',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='transmittal',
            name='contractor',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='transmittal',
            name='rejected_dir',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='transmittal',
            name='tobechecked_dir',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
