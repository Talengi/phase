# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_user_is_external'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_external',
            field=models.BooleanField(default=False, help_text='Used to tell apart regular users and externals ones (contractors).', verbose_name='External User'),
        ),
    ]
