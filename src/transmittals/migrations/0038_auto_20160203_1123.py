# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.files.storage
import transmittals.fields


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0037_auto_20160203_1108'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trsrevision',
            name='native_file',
            field=transmittals.fields.TransmittalFileField(upload_to=transmittals.fields.transmittal_upload_to, storage=django.core.files.storage.FileSystemStorage(base_url='/private/', location='/Users/laurentpaoletti/Documents/DEV/DJ/phase/private'), max_length=255, blank=True, null=True, verbose_name='Native file'),
        ),
    ]
