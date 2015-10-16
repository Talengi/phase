# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exports', '0002_auto_20150918_1449'),
    ]

    operations = [
        migrations.AddField(
            model_name='export',
            name='format',
            field=models.CharField(default='csv', max_length=5, verbose_name='Format', choices=[('csv', 'csv'), ('pdf', 'pdf')]),
        ),
    ]
