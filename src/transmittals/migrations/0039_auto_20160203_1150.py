# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.files.storage
import documents.fileutils
import documents.fields


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0038_auto_20160203_1123'),
    ]

    operations = [
        migrations.AlterField(
            model_name='outgoingtransmittalrevision',
            name='native_file',
            field=documents.fields.RevisionFileField(upload_to=documents.fileutils.revision_file_path, storage=django.core.files.storage.FileSystemStorage(base_url='/private/', location='/Users/laurentpaoletti/Documents/DEV/DJ/phase/private'), max_length=255, blank=True, null=True, verbose_name='Native File'),
        ),
        migrations.AlterField(
            model_name='transmittalrevision',
            name='native_file',
            field=documents.fields.RevisionFileField(upload_to=documents.fileutils.revision_file_path, storage=django.core.files.storage.FileSystemStorage(base_url='/private/', location='/Users/laurentpaoletti/Documents/DEV/DJ/phase/private'), max_length=255, blank=True, null=True, verbose_name='Native File'),
        ),
    ]
