# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0029_auto_20160203_1221'),
    ]

    operations = [
        migrations.AddField(
            model_name='correspondence',
            name='contract_number_new',
            field=models.CharField(default='XYZ', max_length=50, verbose_name='Contract Number'),
            preserve_default=False,
        ),
    ]
