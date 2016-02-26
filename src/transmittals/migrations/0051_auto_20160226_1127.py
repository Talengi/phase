# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0050_make_entities'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trsrevision',
            name='originator_new',
            field=models.ForeignKey(verbose_name='Originator', to='accounts.Entity'),
        ),
    ]
