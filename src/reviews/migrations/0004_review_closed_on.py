# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0003_review_return_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='closed_on',
            field=models.DateTimeField(null=True, verbose_name='Closed on', blank=True),
        ),
    ]
