# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import privatemedia.fileutils
import privatemedia.fields
import reviews.fileutils


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0014_auto_20160129_0920'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='comments',
            field=privatemedia.fields.ProtectedFileField(storage=privatemedia.fileutils.ProtectedStorage(), upload_to=reviews.fileutils.review_comments_file_path, null=True, verbose_name='Comments', blank=True),
        ),
    ]
