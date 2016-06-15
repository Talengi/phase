# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0010_auto_20160202_1624'),
    ]

    operations = [
        migrations.AddField(
            model_name='categorytemplate',
            name='display_reporting',
            field=models.BooleanField(default=False, verbose_name='Display reporting section'),
        ),
    ]
