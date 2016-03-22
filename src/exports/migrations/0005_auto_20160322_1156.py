# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exports', '0004_move_exports_dir'),
    ]

    operations = [
        migrations.AlterField(
            model_name='export',
            name='format',
            field=models.CharField(default='csv', max_length=5, verbose_name='Format', choices=[('csv', 'csv'), ('pdf', 'pdf'), ('xlsx', 'xlsx')]),
        ),
    ]
