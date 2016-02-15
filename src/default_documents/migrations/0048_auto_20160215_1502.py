# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0047_auto_20160211_0835'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contractordeliverablerevision',
            old_name='trs_comments',
            new_name='file_transmitted',
        ),
    ]
