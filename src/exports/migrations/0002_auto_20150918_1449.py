# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exports', '0001_squashed_0003_auto_20150915_1132'),
    ]

    operations = [
        migrations.AlterField(
            model_name='export',
            name='querystring',
            field=models.TextField(default='', help_text='The search filter querystring', verbose_name='Querystring', blank=True),
        ),
    ]
