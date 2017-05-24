# -*- coding: utf-8 -*-


import os
from os import path

from django.db import migrations
from django.conf import settings

import privatemedia.fields
import privatemedia.storage
import reviews.fileutils


def move_files_to_private_dir(*args):
    protected_root = settings.PROTECTED_ROOT
    reviews_dir = path.join(protected_root, 'reviews')

    private_root = settings.PRIVATE_ROOT
    new_dir = path.join(private_root, 'reviews')

    if os.path.exists(reviews_dir):
        os.rename(reviews_dir, new_dir)


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0015_auto_20160209_0821'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='comments',
            field=privatemedia.fields.PrivateFileField(storage=privatemedia.storage.ProtectedStorage(), upload_to=reviews.fileutils.review_comments_file_path, null=True, verbose_name='Comments', blank=True),
        ),
        migrations.RunPython(move_files_to_private_dir)
    ]
