# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0007_auto_20150914_1021'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='review',
            unique_together=set([('reviewer', 'document', 'revision')]),
        ),
    ]
