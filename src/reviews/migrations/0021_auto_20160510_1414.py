# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0020_auto_20160510_1104'),
        ('distriblists', '0002_copy_lists_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='distributionlist',
            name='approver',
        ),
        migrations.RemoveField(
            model_name='distributionlist',
            name='categories',
        ),
        migrations.RemoveField(
            model_name='distributionlist',
            name='leader',
        ),
        migrations.RemoveField(
            model_name='distributionlist',
            name='reviewers',
        ),
        migrations.DeleteModel(
            name='DistributionList',
        ),
    ]
