# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0025_auto_20160202_1856'),
    ]

    operations = [
        migrations.AddField(
            model_name='transmittal',
            name='contract_number_new',
            field=models.CharField(default='XYZ', max_length=50, verbose_name='Contract Number'),
            preserve_default=False,
        ),
    ]
