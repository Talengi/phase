# -*- coding: utf-8 -*-


from django.db import models, migrations
import privatemedia.fields
import metadata.fields
import django.core.files.storage
import reviews.fileutils


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0005_auto_20150914_1450'),
    ]

    operations = [
        migrations.AddField(
            model_name='contractordeliverablerevision',
            name='dc_comments',
            field=privatemedia.fields.PrivateFileField(storage=django.core.files.storage.FileSystemStorage(base_url='/private/', location='/home/thibault/code/phase/private'), upload_to=reviews.fileutils.dc_review_comments_file_path, null=True, verbose_name='Comments', blank=True),
        ),
        migrations.AddField(
            model_name='contractordeliverablerevision',
            name='dc_return_code',
            field=metadata.fields.ConfigurableChoiceField(max_length=3, null=True, verbose_name='DC Return code', list_index='REVIEW_RETURN_CODES', blank=True),
        ),
        migrations.AddField(
            model_name='demometadatarevision',
            name='dc_comments',
            field=privatemedia.fields.PrivateFileField(storage=django.core.files.storage.FileSystemStorage(base_url='/private/', location='/home/thibault/code/phase/private'), upload_to=reviews.fileutils.dc_review_comments_file_path, null=True, verbose_name='Comments', blank=True),
        ),
        migrations.AddField(
            model_name='demometadatarevision',
            name='dc_return_code',
            field=metadata.fields.ConfigurableChoiceField(max_length=3, null=True, verbose_name='DC Return code', list_index='REVIEW_RETURN_CODES', blank=True),
        ),
    ]
