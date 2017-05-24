# -*- coding: utf-8 -*-


from django.db import models, migrations
import privatemedia.fields
import transmittals.fileutils
import django.core.files.storage


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0020_auto_20160120_1124'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contractordeliverablerevision',
            name='purpose_of_issue',
            field=models.CharField(default='FR', max_length=2, verbose_name='Purpose of issue', blank=True, choices=[('FR', 'For review'), ('FI', 'For information')]),
        ),
        migrations.AlterField(
            model_name='contractordeliverablerevision',
            name='trs_comments',
            field=privatemedia.fields.PrivateFileField(storage=django.core.files.storage.FileSystemStorage(base_url='/private/', location='/home/thibault/code/phase/private'), upload_to=transmittals.fileutils.trs_comments_file_path, null=True, verbose_name='File Transmitted', blank=True),
        ),
    ]
