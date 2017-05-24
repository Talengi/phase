# -*- coding: utf-8 -*-


from django.db import models, migrations
import transmittals.fields
import metadata.fields
import documents.fileutils
import documents.fields
import django.utils.timezone
import django.core.files.storage
import default_documents.validators


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0001_initial'),
        ('categories', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transmittal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('document_key', models.SlugField(unique=True, max_length=250, verbose_name='Document number')),
                ('transmittal_key', models.CharField(max_length=250, verbose_name='Transmittal key')),
                ('transmittal_date', models.DateField(null=True, verbose_name='Transmittal date', blank=True)),
                ('ack_of_receipt_date', models.DateField(null=True, verbose_name='Acknowledgment of receipt date', blank=True)),
                ('contract_number', metadata.fields.ConfigurableChoiceField(max_length=8, verbose_name='Contract Number', list_index='CONTRACT_NBS')),
                ('originator', metadata.fields.ConfigurableChoiceField(default='CTR', max_length=3, verbose_name='Originator', list_index='ORIGINATORS')),
                ('recipient', metadata.fields.ConfigurableChoiceField(max_length=50, verbose_name='Recipient', list_index='RECIPIENTS')),
                ('sequential_number', models.PositiveIntegerField(null=True, verbose_name='sequential number', blank=True)),
                ('document_type', metadata.fields.ConfigurableChoiceField(default='PID', max_length=3, verbose_name='Document Type', list_index='DOCUMENT_TYPES')),
                ('status', models.CharField(default='tobechecked', max_length=20, choices=[('new', 'New'), ('invalid', 'Invalid'), ('tobechecked', 'To be checked'), ('rejected', 'Rejected'), ('processing', 'Processing'), ('accepted', 'Accepted')])),
                ('contractor', models.CharField(max_length=255)),
                ('tobechecked_dir', models.CharField(max_length=255)),
                ('accepted_dir', models.CharField(max_length=255)),
                ('rejected_dir', models.CharField(max_length=255)),
                ('document', models.OneToOneField(to='documents.Document')),
            ],
            options={
                'ordering': ('document_key',),
                'verbose_name': 'Transmittal',
                'verbose_name_plural': 'Transmittals',
            },
        ),
        migrations.CreateModel(
            name='TransmittalRevision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('revision', models.PositiveIntegerField(default=0, verbose_name='Revision')),
                ('revision_date', models.DateField(null=True, verbose_name='Revision Date', blank=True)),
                ('native_file', documents.fields.RevisionFileField(storage=django.core.files.storage.FileSystemStorage(base_url='/private/', location='/home/thibault/code/phase/private'), upload_to=documents.fileutils.revision_file_path, null=True, verbose_name='Native File', blank=True)),
                ('pdf_file', documents.fields.RevisionFileField(storage=django.core.files.storage.FileSystemStorage(base_url='/private/', location='/home/thibault/code/phase/private'), upload_to=documents.fileutils.revision_file_path, null=True, verbose_name='PDF File', blank=True)),
                ('received_date', models.DateField(verbose_name='Received date')),
                ('created_on', models.DateField(default=django.utils.timezone.now, verbose_name='Created on')),
                ('updated_on', models.DateTimeField(auto_now=True, verbose_name='Updated on')),
                ('trs_status', metadata.fields.ConfigurableChoiceField(default='opened', max_length=20, verbose_name='Status', list_index='STATUS_TRANSMITTALS')),
                ('document', models.ForeignKey(to='documents.Document')),
            ],
            options={
                'ordering': ('-revision',),
                'abstract': False,
                'get_latest_by': 'revision',
            },
        ),
        migrations.CreateModel(
            name='TrsRevision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('document_key', models.SlugField(max_length=250, verbose_name='Document number')),
                ('title', models.TextField(verbose_name='Title')),
                ('revision', models.PositiveIntegerField(default=0, verbose_name='Revision')),
                ('revision_date', models.DateField(null=True, verbose_name='Revision date', blank=True)),
                ('received_date', models.DateField(null=True, verbose_name='Received date', blank=True)),
                ('created_on', models.DateField(null=True, verbose_name='Created on', blank=True)),
                ('accepted', models.NullBooleanField(verbose_name='Accepted?')),
                ('comment', models.TextField(null=True, verbose_name='Comment', blank=True)),
                ('is_new_revision', models.BooleanField(verbose_name='Is new revision?')),
                ('contract_number', metadata.fields.ConfigurableChoiceField(max_length=8, verbose_name='Contract Number', list_index='CONTRACT_NBS')),
                ('originator', metadata.fields.ConfigurableChoiceField(default='FWF', max_length=3, verbose_name='Originator', list_index='ORIGINATORS')),
                ('unit', metadata.fields.ConfigurableChoiceField(default='000', max_length=3, verbose_name='Unit', list_index='UNITS')),
                ('discipline', metadata.fields.ConfigurableChoiceField(default='PCS', max_length=3, verbose_name='Discipline', list_index='DISCIPLINES')),
                ('document_type', metadata.fields.ConfigurableChoiceField(default='PID', max_length=3, verbose_name='Document Type', list_index='DOCUMENT_TYPES')),
                ('sequential_number', models.CharField(default='0001', validators=[default_documents.validators.StringNumberValidator(length=4)], max_length=4, blank=True, help_text='Select a four digit number', null=True, verbose_name='sequential Number')),
                ('system', metadata.fields.ConfigurableChoiceField(max_length=50, null=True, verbose_name='System', list_index='SYSTEMS', blank=True)),
                ('wbs', metadata.fields.ConfigurableChoiceField(max_length=20, null=True, verbose_name='Wbs', list_index='WBS', blank=True)),
                ('weight', models.IntegerField(null=True, verbose_name='Weight', blank=True)),
                ('docclass', models.IntegerField(default=1, verbose_name='Class', choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4')])),
                ('status', metadata.fields.ConfigurableChoiceField(list_index='STATUSES', default='STD', max_length=3, blank=True, null=True, verbose_name='Status')),
                ('return_code', models.PositiveIntegerField(null=True, verbose_name='Return code', blank=True)),
                ('review_start_date', models.DateField(null=True, verbose_name='Review start date', blank=True)),
                ('review_due_date', models.DateField(null=True, verbose_name='Review due date', blank=True)),
                ('review_leader', models.CharField(max_length=150, null=True, verbose_name='Review leader', blank=True)),
                ('leader_comment_date', models.DateField(null=True, verbose_name='Leader comment date', blank=True)),
                ('review_approver', models.CharField(max_length=150, null=True, verbose_name='Review approver', blank=True)),
                ('approver_comment_date', models.DateField(null=True, verbose_name='Approver comment date', blank=True)),
                ('review_trs', models.CharField(max_length=255, null=True, verbose_name='Review transmittal name', blank=True)),
                ('review_trs_status', models.CharField(max_length=50, null=True, verbose_name='Review transmittal status', blank=True)),
                ('outgoing_trs', models.CharField(max_length=255, null=True, verbose_name='Outgoing transmittal name', blank=True)),
                ('outgoing_trs_status', models.CharField(max_length=50, null=True, verbose_name='Outgoing transmittal status', blank=True)),
                ('outgoing_trs_sent_date', models.DateField(null=True, verbose_name='Outgoing transmittal sent date', blank=True)),
                ('doc_category', models.CharField(max_length=50, verbose_name='Doc category')),
                ('pdf_file', transmittals.fields.TransmittalFileField(upload_to=transmittals.fields.transmittal_upload_to, storage=django.core.files.storage.FileSystemStorage(base_url='/private/', location='/home/thibault/code/phase/private'), verbose_name='Pdf file')),
                ('native_file', transmittals.fields.TransmittalFileField(storage=django.core.files.storage.FileSystemStorage(base_url='/private/', location='/home/thibault/code/phase/private'), upload_to=transmittals.fields.transmittal_upload_to, null=True, verbose_name='Native file', blank=True)),
                ('category', models.ForeignKey(to='categories.Category')),
                ('document', models.ForeignKey(verbose_name='Document', blank=True, to='documents.Document', null=True)),
                ('transmittal', models.ForeignKey(verbose_name='Transmittal', to='transmittals.Transmittal')),
            ],
            options={
                'verbose_name': 'Trs Revision',
                'verbose_name_plural': 'Trs Revisions',
            },
        ),
        migrations.AddField(
            model_name='transmittal',
            name='latest_revision',
            field=models.ForeignKey(verbose_name='Latest revision', to='transmittals.TransmittalRevision'),
        ),
        migrations.AddField(
            model_name='transmittal',
            name='related_documents',
            field=models.ManyToManyField(related_name='transmittals_related_set', to='documents.Document', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='trsrevision',
            unique_together=set([('transmittal', 'document_key', 'revision')]),
        ),
        migrations.AlterUniqueTogether(
            name='transmittalrevision',
            unique_together=set([('document', 'revision')]),
        ),
        migrations.AlterIndexTogether(
            name='transmittal',
            index_together=set([('contract_number', 'originator', 'recipient', 'sequential_number', 'status')]),
        ),
    ]
