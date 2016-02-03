# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0020_auto_20160112_0941'),
    ]

    operations = [
        migrations.AddField(
            model_name='outgoingtransmittal',
            name='contract_number_new',
            field=models.CharField(default='XYZ', max_length=50, verbose_name='Contract Number'),
            preserve_default=False,
        ),
    ]
