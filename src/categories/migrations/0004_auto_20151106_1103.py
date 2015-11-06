# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0003_assign_trigrams'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organisation',
            name='trigram',
            field=models.CharField(default='ABC', unique=True, max_length=3, verbose_name='Trigram'),
            preserve_default=False,
        ),
    ]
