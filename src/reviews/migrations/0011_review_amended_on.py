# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0010_auto_20150929_1544'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='amended_on',
            field=models.DateTimeField(null=True, verbose_name='Amended on', blank=True),
        ),
    ]
