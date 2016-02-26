# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0052_remove_trsrevision_originator'),
    ]

    operations = [
        migrations.RenameField(
            model_name='trsrevision',
            old_name='originator_new',
            new_name='originator',
        ),
    ]
