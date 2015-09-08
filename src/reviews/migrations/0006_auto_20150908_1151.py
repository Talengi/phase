# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0005_save_review_close_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='review',
            name='closed',
        ),
        migrations.RemoveField(
            model_name='review',
            name='reviewed_on',
        ),
    ]
