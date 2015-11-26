# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import privatemedia.fields
import transmittals.fileutils
import django.core.files.storage


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0010_contractordeliverablerevision_trs_comments'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contractordeliverablerevision',
            name='trs_comments',
            field=privatemedia.fields.PrivateFileField(storage=django.core.files.storage.FileSystemStorage(base_url='/private/', location='/home/thibault/code/phase/private'), upload_to=transmittals.fileutils.trs_comments_file_path, null=True, verbose_name='Final comments', blank=True),
        ),
    ]
