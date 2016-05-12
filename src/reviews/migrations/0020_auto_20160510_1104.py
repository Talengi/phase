# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0019_auto_20160415_0919'),
    ]

    operations = [
        migrations.AlterField(
            model_name='distributionlist',
            name='name',
            field=models.CharField(unique=True, max_length=250, verbose_name='Name'),
        ),
    ]
