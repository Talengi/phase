# -*- coding: utf-8 -*-


from django.db import models, migrations
import privatemedia.fields
import transmittals.fileutils
import django.core.files.storage


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0009_auto_20151104_1002'),
    ]

    operations = [
        migrations.AddField(
            model_name='contractordeliverablerevision',
            name='trs_comments',
            field=privatemedia.fields.PrivateFileField(storage=django.core.files.storage.FileSystemStorage(base_url='/private/', location='/home/thibault/code/phase/private'), upload_to=transmittals.fileutils.trs_comments_file_path, null=True, verbose_name='Comments', blank=True),
        ),
    ]
