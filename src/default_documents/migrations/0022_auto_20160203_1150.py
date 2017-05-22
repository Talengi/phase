# -*- coding: utf-8 -*-


from django.db import migrations, models
import django.core.files.storage
import documents.fileutils
import documents.fields


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0021_auto_20160122_1131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contractordeliverablerevision',
            name='native_file',
            field=documents.fields.RevisionFileField(upload_to=documents.fileutils.revision_file_path, storage=django.core.files.storage.FileSystemStorage(base_url='/private/', location='/Users/laurentpaoletti/Documents/DEV/DJ/phase/private'), max_length=255, blank=True, null=True, verbose_name='Native File'),
        ),
        migrations.AlterField(
            model_name='correspondencerevision',
            name='native_file',
            field=documents.fields.RevisionFileField(upload_to=documents.fileutils.revision_file_path, storage=django.core.files.storage.FileSystemStorage(base_url='/private/', location='/Users/laurentpaoletti/Documents/DEV/DJ/phase/private'), max_length=255, blank=True, null=True, verbose_name='Native File'),
        ),
        migrations.AlterField(
            model_name='demometadatarevision',
            name='native_file',
            field=documents.fields.RevisionFileField(upload_to=documents.fileutils.revision_file_path, storage=django.core.files.storage.FileSystemStorage(base_url='/private/', location='/Users/laurentpaoletti/Documents/DEV/DJ/phase/private'), max_length=255, blank=True, null=True, verbose_name='Native File'),
        ),
        migrations.AlterField(
            model_name='minutesofmeetingrevision',
            name='native_file',
            field=documents.fields.RevisionFileField(upload_to=documents.fileutils.revision_file_path, storage=django.core.files.storage.FileSystemStorage(base_url='/private/', location='/Users/laurentpaoletti/Documents/DEV/DJ/phase/private'), max_length=255, blank=True, null=True, verbose_name='Native File'),
        ),
    ]
