# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.db import migrations
from django.conf import settings
import privatemedia.fields
import privatemedia.storage
import transmittals.fileutils


def move_dirs(*args):
    protected_root = settings.PROTECTED_ROOT
    private_root = settings.PRIVATE_ROOT
    exports_dir = os.path.join(protected_root, 'transmittals')
    new_dir = os.path.join(private_root, 'transmittals')

    os.rename(exports_dir, new_dir)


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0046_auto_20160209_0821'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contractordeliverablerevision',
            name='trs_comments',
            field=privatemedia.fields.PrivateFileField(storage=privatemedia.storage.ProtectedStorage(), upload_to=transmittals.fileutils.trs_comments_file_path, null=True, verbose_name='File Transmitted', blank=True),
        ),
        migrations.RunPython(move_dirs)
    ]
