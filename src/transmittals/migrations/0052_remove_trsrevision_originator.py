# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0051_auto_20160226_1127'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trsrevision',
            name='originator',
        ),
    ]
