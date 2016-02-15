# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import privatemedia.fields
import privatemedia.storage
import transmittals.fileutils


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0048_auto_20160215_1502'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contractordeliverablerevision',
            name='file_transmitted',
            field=privatemedia.fields.PrivateFileField(storage=privatemedia.storage.ProtectedStorage(), upload_to=transmittals.fileutils.file_transmitted_file_path, null=True, verbose_name='File Transmitted', blank=True),
        ),
    ]
