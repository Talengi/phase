# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exports', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='export',
            name='status',
            field=models.CharField(default='new', max_length=30, verbose_name='Status', choices=[('new', 'New'), ('processing', 'Processing'), ('done', 'Done')]),
        ),
    ]
