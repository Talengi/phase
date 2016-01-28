# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0008_auto_20151127_1124'),
        ('reviews', '0012_distributionlist'),
    ]

    operations = [
        migrations.AddField(
            model_name='distributionlist',
            name='category',
            field=models.ForeignKey(default=1, verbose_name='Category', to='categories.Category'),
            preserve_default=False,
        ),
    ]
