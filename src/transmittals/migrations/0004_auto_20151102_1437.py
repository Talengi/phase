# -*- coding: utf-8 -*-


from django.db import models, migrations
import documents.fileutils
import metadata.fields
import django.utils.timezone
import django.core.files.storage
import documents.fields


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0002_document_favorited_by'),
        ('transmittals', '0003_auto_20151015_1501'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExportedRevision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('revision', models.PositiveIntegerField(verbose_name='Revision')),
                ('title', models.TextField(verbose_name='Title')),
                ('status', models.CharField(max_length=5, verbose_name='Status')),
                ('return_code', models.CharField(max_length=5, verbose_name='Return code')),
                ('document', models.ForeignKey(to='documents.Document')),
            ],
            options={
                'verbose_name': 'Exported revision',
                'verbose_name_plural': 'Exported revisions',
            },
        ),
        migrations.CreateModel(
            name='OutgoingTransmittal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('document_key', models.SlugField(unique=True, max_length=250, verbose_name='Document number')),
                ('contract_number', metadata.fields.ConfigurableChoiceField(max_length=8, verbose_name='Contract Number', list_index='CONTRACT_NBS')),
                ('originator', metadata.fields.ConfigurableChoiceField(default='CTR', max_length=3, verbose_name='Originator', list_index='ORIGINATORS')),
                ('recipient', metadata.fields.ConfigurableChoiceField(max_length=50, verbose_name='Recipient', list_index='RECIPIENTS')),
                ('sequential_number', models.PositiveIntegerField(null=True, verbose_name='sequential number', blank=True)),
                ('document', models.OneToOneField(to='documents.Document')),
            ],
            options={
                'ordering': ('document_key',),
                'verbose_name': 'Transmittal',
                'verbose_name_plural': 'Transmittals',
            },
        ),
        migrations.CreateModel(
            name='OutgoingTransmittalRevision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('revision', models.PositiveIntegerField(default=0, verbose_name='Revision')),
                ('revision_date', models.DateField(null=True, verbose_name='Revision Date', blank=True)),
                ('native_file', documents.fields.RevisionFileField(storage=django.core.files.storage.FileSystemStorage(base_url='/private/', location='/home/thibault/code/phase/private'), upload_to=documents.fileutils.revision_file_path, null=True, verbose_name='Native File', blank=True)),
                ('pdf_file', documents.fields.RevisionFileField(storage=django.core.files.storage.FileSystemStorage(base_url='/private/', location='/home/thibault/code/phase/private'), upload_to=documents.fileutils.revision_file_path, null=True, verbose_name='PDF File', blank=True)),
                ('received_date', models.DateField(verbose_name='Received date')),
                ('created_on', models.DateField(default=django.utils.timezone.now, verbose_name='Created on')),
                ('updated_on', models.DateTimeField(auto_now=True, verbose_name='Updated on')),
                ('document', models.ForeignKey(to='documents.Document')),
            ],
            options={
                'ordering': ('-revision',),
                'abstract': False,
                'get_latest_by': 'revision',
            },
        ),
        migrations.AddField(
            model_name='outgoingtransmittal',
            name='latest_revision',
            field=models.ForeignKey(verbose_name='Latest revision', to='transmittals.OutgoingTransmittalRevision'),
        ),
        migrations.AddField(
            model_name='outgoingtransmittal',
            name='related_revisions',
            field=models.ManyToManyField(related_name='outgoing_transmittal_set', through='transmittals.ExportedRevision', to='documents.Document', blank=True),
        ),
        migrations.AddField(
            model_name='exportedrevision',
            name='transmittal',
            field=models.ForeignKey(to='transmittals.OutgoingTransmittal'),
        ),
        migrations.AlterUniqueTogether(
            name='outgoingtransmittalrevision',
            unique_together=set([('document', 'revision')]),
        ),
    ]
