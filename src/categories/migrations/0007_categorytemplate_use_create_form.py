# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0006_auto_20151125_1114'),
    ]

    operations = [
        migrations.AddField(
            model_name='categorytemplate',
            name='use_create_form',
            field=models.BooleanField(default=True, verbose_name='Use document creation form'),
        ),
    ]
