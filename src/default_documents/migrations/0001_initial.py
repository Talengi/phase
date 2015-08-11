# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import metadata.fields
import documents.fileutils
import documents.fields
import django.utils.timezone
import django.core.files.storage
import default_documents.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ContractorDeliverable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('document_key', models.SlugField(unique=True, max_length=250, verbose_name='Document number')),
                ('title', models.TextField(verbose_name='Title')),
                ('contract_number', metadata.fields.ConfigurableChoiceField(max_length=15, verbose_name='Contract Number', list_index=b'CONTRACT_NBS')),
                ('originator', metadata.fields.ConfigurableChoiceField(default='FWF', max_length=3, verbose_name='Originator', list_index=b'ORIGINATORS')),
                ('unit', metadata.fields.ConfigurableChoiceField(default=b'000', max_length=3, verbose_name='Unit', list_index=b'UNITS')),
                ('discipline', metadata.fields.ConfigurableChoiceField(default=b'PCS', max_length=3, verbose_name='Discipline', list_index=b'DISCIPLINES')),
                ('document_type', metadata.fields.ConfigurableChoiceField(default=b'PID', max_length=3, verbose_name='Document Type', list_index=b'DOCUMENT_TYPES')),
                ('sequential_number', models.CharField(default='0001', help_text='Select a four digit number', max_length=4, verbose_name='sequential Number', validators=[default_documents.validators.StringNumberValidator(length=4)])),
                ('system', metadata.fields.ConfigurableChoiceField(max_length=50, null=True, verbose_name='System', list_index=b'SYSTEMS', blank=True)),
                ('wbs', metadata.fields.ConfigurableChoiceField(max_length=20, null=True, verbose_name='WBS', list_index=b'WBS', blank=True)),
                ('weight', models.IntegerField(null=True, verbose_name='Weight', blank=True)),
                ('status_std_planned_date', models.DateField(null=True, verbose_name='Status STD Planned Date', blank=True)),
                ('status_std_forecast_date', models.DateField(null=True, verbose_name='Status STD Forecast Date', blank=True)),
                ('status_std_actual_date', models.DateField(null=True, verbose_name='Status STD Actual Date', blank=True)),
                ('status_idc_planned_date', models.DateField(null=True, verbose_name='Status IDC Planned Date', blank=True)),
                ('status_idc_forecast_date', models.DateField(null=True, verbose_name='Status IDC Forecast Date', blank=True)),
                ('status_idc_actual_date', models.DateField(null=True, verbose_name='Status IDC Actual Date', blank=True)),
                ('status_ifr_planned_date', models.DateField(null=True, verbose_name='Status IFR Planned Date', blank=True)),
                ('status_ifr_forecast_date', models.DateField(null=True, verbose_name='Status IFR Forecast Date', blank=True)),
                ('status_ifr_actual_date', models.DateField(null=True, verbose_name='Status IFR Actual Date', blank=True)),
                ('status_ifa_planned_date', models.DateField(null=True, verbose_name='Status IFA Planned Date', blank=True)),
                ('status_ifa_forecast_date', models.DateField(null=True, verbose_name='Status IFA Forecast Date', blank=True)),
                ('status_ifa_actual_date', models.DateField(null=True, verbose_name='Status IFA Actual Date', blank=True)),
                ('status_ifd_planned_date', models.DateField(null=True, verbose_name='Status IFD Planned Date', blank=True)),
                ('status_ifd_forecast_date', models.DateField(null=True, verbose_name='Status IFD Forecast Date', blank=True)),
                ('status_ifd_actual_date', models.DateField(null=True, verbose_name='Status IFD Actual Date', blank=True)),
                ('status_ifc_planned_date', models.DateField(null=True, verbose_name='Status IFC Planned Date', blank=True)),
                ('status_ifc_forecast_date', models.DateField(null=True, verbose_name='Status IFC Forecast Date', blank=True)),
                ('status_ifc_actual_date', models.DateField(null=True, verbose_name='Status IFC Actual Date', blank=True)),
                ('status_ifi_planned_date', models.DateField(null=True, verbose_name='Status IFI Planned Date', blank=True)),
                ('status_ifi_forecast_date', models.DateField(null=True, verbose_name='Status IFI Forecast Date', blank=True)),
                ('status_ifi_actual_date', models.DateField(null=True, verbose_name='Status IFI Actual Date', blank=True)),
                ('status_asb_planned_date', models.DateField(null=True, verbose_name='Status ASB Planned Date', blank=True)),
                ('status_asb_forecast_date', models.DateField(null=True, verbose_name='Status ASB Forecast Date', blank=True)),
                ('status_asb_actual_date', models.DateField(null=True, verbose_name='Status ASB Actual Date', blank=True)),
            ],
            options={
                'ordering': ('document_key',),
            },
        ),
        migrations.CreateModel(
            name='ContractorDeliverableRevision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('revision', models.PositiveIntegerField(default=0, verbose_name='Revision')),
                ('revision_date', models.DateField(null=True, verbose_name='Revision Date', blank=True)),
                ('native_file', documents.fields.RevisionFileField(storage=django.core.files.storage.FileSystemStorage(base_url='/private/', location='/home/thibault/code/phase/private'), upload_to=documents.fileutils.revision_file_path, null=True, verbose_name='Native File', blank=True)),
                ('pdf_file', documents.fields.RevisionFileField(storage=django.core.files.storage.FileSystemStorage(base_url='/private/', location='/home/thibault/code/phase/private'), upload_to=documents.fileutils.revision_file_path, null=True, verbose_name='PDF File', blank=True)),
                ('received_date', models.DateField(verbose_name='Received date')),
                ('created_on', models.DateField(default=django.utils.timezone.now, verbose_name='Created on')),
                ('updated_on', models.DateTimeField(auto_now=True, verbose_name='Updated on')),
                ('review_start_date', models.DateField(null=True, verbose_name='Review start date', blank=True)),
                ('review_due_date', models.DateField(null=True, verbose_name='Review due date', blank=True)),
                ('reviewers_step_closed', models.DateField(verbose_name='Reviewers step closed', blank=True)),
                ('leader_step_closed', models.DateField(null=True, verbose_name='Leader step closed', blank=True)),
                ('review_end_date', models.DateField(null=True, verbose_name='Review end date', blank=True)),
                ('docclass', models.IntegerField(default=1, verbose_name='Class', choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4')])),
                ('return_code', models.IntegerField(null=True, verbose_name='Return code', blank=True)),
                ('status', metadata.fields.ConfigurableChoiceField(list_index=b'STATUSES', default=b'STD', max_length=3, blank=True, null=True, verbose_name='Status')),
                ('final_revision', models.NullBooleanField(verbose_name='Is final revision?', choices=[(True, 'Yes'), (False, 'No')])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Correspondence',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('document_key', models.SlugField(unique=True, max_length=250, verbose_name='Document number')),
                ('subject', models.TextField(verbose_name='Subject')),
                ('correspondence_date', models.DateField(verbose_name='Correspondence date')),
                ('received_sent_date', models.DateField(verbose_name='Received / sent date')),
                ('contract_number', metadata.fields.ConfigurableChoiceField(max_length=8, verbose_name='Contract Number', list_index=b'CONTRACT_NBS')),
                ('originator', metadata.fields.ConfigurableChoiceField(default=b'FWF', max_length=3, verbose_name='Originator', list_index=b'ORIGINATORS')),
                ('recipient', metadata.fields.ConfigurableChoiceField(max_length=50, verbose_name='Recipient', list_index=b'RECIPIENTS')),
                ('document_type', metadata.fields.ConfigurableChoiceField(default=b'PID', max_length=3, verbose_name='Document Type', list_index=b'DOCUMENT_TYPES')),
                ('sequential_number', models.CharField(default='0001', help_text='Type in a four digit number', max_length=4, verbose_name='sequential Number', validators=[default_documents.validators.StringNumberValidator(length=4)])),
                ('author', metadata.fields.ConfigurableChoiceField(max_length=250, null=True, verbose_name='Author', list_index=b'AUTHORS', blank=True)),
                ('addresses', metadata.fields.ConfigurableChoiceField(max_length=50, null=True, verbose_name='Addresses', list_index=b'ADDRESSES', blank=True)),
                ('response_required', models.NullBooleanField(verbose_name='Response required')),
                ('due_date', models.DateField(null=True, verbose_name='Due date', blank=True)),
                ('external_reference', models.TextField(null=True, verbose_name='External reference', blank=True)),
            ],
            options={
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='CorrespondenceRevision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('revision', models.PositiveIntegerField(default=0, verbose_name='Revision')),
                ('revision_date', models.DateField(null=True, verbose_name='Revision Date', blank=True)),
                ('native_file', documents.fields.RevisionFileField(storage=django.core.files.storage.FileSystemStorage(base_url='/private/', location='/home/thibault/code/phase/private'), upload_to=documents.fileutils.revision_file_path, null=True, verbose_name='Native File', blank=True)),
                ('pdf_file', documents.fields.RevisionFileField(storage=django.core.files.storage.FileSystemStorage(base_url='/private/', location='/home/thibault/code/phase/private'), upload_to=documents.fileutils.revision_file_path, null=True, verbose_name='PDF File', blank=True)),
                ('received_date', models.DateField(verbose_name='Received date')),
                ('created_on', models.DateField(default=django.utils.timezone.now, verbose_name='Created on')),
                ('updated_on', models.DateTimeField(auto_now=True, verbose_name='Updated on')),
                ('status', metadata.fields.ConfigurableChoiceField(max_length=20, verbose_name='Status', list_index=b'STATUS_COR_MOM')),
                ('under_review', models.NullBooleanField(verbose_name='Under Review', choices=[(True, 'Yes'), (False, 'No')])),
                ('overdue', models.NullBooleanField(verbose_name='Overdue', choices=[(True, 'Yes'), (False, 'No')])),
            ],
            options={
                'ordering': ('-revision',),
                'abstract': False,
                'get_latest_by': 'revision',
            },
        ),
        migrations.CreateModel(
            name='DemoMetadata',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('document_key', models.SlugField(unique=True, max_length=250, verbose_name='Document number')),
                ('title', models.CharField(max_length=250, verbose_name='Title')),
            ],
            options={
                'ordering': ('document_key',),
            },
        ),
        migrations.CreateModel(
            name='DemoMetadataRevision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('revision', models.PositiveIntegerField(default=0, verbose_name='Revision')),
                ('revision_date', models.DateField(null=True, verbose_name='Revision Date', blank=True)),
                ('native_file', documents.fields.RevisionFileField(storage=django.core.files.storage.FileSystemStorage(base_url='/private/', location='/home/thibault/code/phase/private'), upload_to=documents.fileutils.revision_file_path, null=True, verbose_name='Native File', blank=True)),
                ('pdf_file', documents.fields.RevisionFileField(storage=django.core.files.storage.FileSystemStorage(base_url='/private/', location='/home/thibault/code/phase/private'), upload_to=documents.fileutils.revision_file_path, null=True, verbose_name='PDF File', blank=True)),
                ('received_date', models.DateField(verbose_name='Received date')),
                ('created_on', models.DateField(default=django.utils.timezone.now, verbose_name='Created on')),
                ('updated_on', models.DateTimeField(auto_now=True, verbose_name='Updated on')),
                ('review_start_date', models.DateField(null=True, verbose_name='Review start date', blank=True)),
                ('review_due_date', models.DateField(null=True, verbose_name='Review due date', blank=True)),
                ('reviewers_step_closed', models.DateField(verbose_name='Reviewers step closed', blank=True)),
                ('leader_step_closed', models.DateField(null=True, verbose_name='Leader step closed', blank=True)),
                ('review_end_date', models.DateField(null=True, verbose_name='Review end date', blank=True)),
                ('docclass', models.IntegerField(default=1, verbose_name='Class', choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4')])),
                ('return_code', models.IntegerField(null=True, verbose_name='Return code', blank=True)),
                ('status', models.CharField(default=b'STD', choices=[(b'STD', b'Started'), (b'IDC', b'Inter Discipline Check'), (b'IFR', b'Issued For Review'), (b'IFA', b'Issued For Approval'), (b'IFD', b'Issued For Design'), (b'IFC', b'Issued For Construction'), (b'FIN', b'Final'), (b'IFI', b'Issued For Information'), (b'ASB', b'As Built'), (b'CLD', b'Cancelled'), (b'SPD', b'Superseded'), (b'ANA', b'Analysis'), (b'BAS', b'Design Basis')], max_length=3, blank=True, null=True, verbose_name='Status')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MinutesOfMeeting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('document_key', models.SlugField(unique=True, max_length=250, verbose_name='Document number')),
                ('subject', models.TextField(verbose_name='Subject')),
                ('meeting_date', models.DateField(verbose_name='Meeting date')),
                ('received_sent_date', models.DateField(verbose_name='Received / sent date')),
                ('contract_number', metadata.fields.ConfigurableChoiceField(max_length=8, verbose_name='Contract Number', list_index=b'CONTRACT_NBS')),
                ('originator', metadata.fields.ConfigurableChoiceField(default=b'FWF', max_length=3, verbose_name='Originator', list_index=b'ORIGINATORS')),
                ('recipient', metadata.fields.ConfigurableChoiceField(max_length=50, verbose_name='Recipient', list_index=b'RECIPIENTS')),
                ('document_type', metadata.fields.ConfigurableChoiceField(default=b'PID', max_length=3, verbose_name='Document Type', list_index=b'DOCUMENT_TYPES')),
                ('sequential_number', models.CharField(default='0001', help_text='Type in a four digit number', max_length=4, verbose_name='sequential Number', validators=[default_documents.validators.StringNumberValidator(length=4)])),
                ('prepared_by', metadata.fields.ConfigurableChoiceField(max_length=250, null=True, verbose_name='Prepared by', list_index=b'AUTHORS', blank=True)),
                ('signed', models.NullBooleanField(verbose_name='Signed', choices=[(True, 'Yes'), (False, 'No')])),
            ],
            options={
                'ordering': ('document_key',),
            },
        ),
        migrations.CreateModel(
            name='MinutesOfMeetingRevision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('revision', models.PositiveIntegerField(default=0, verbose_name='Revision')),
                ('revision_date', models.DateField(null=True, verbose_name='Revision Date', blank=True)),
                ('native_file', documents.fields.RevisionFileField(storage=django.core.files.storage.FileSystemStorage(base_url='/private/', location='/home/thibault/code/phase/private'), upload_to=documents.fileutils.revision_file_path, null=True, verbose_name='Native File', blank=True)),
                ('pdf_file', documents.fields.RevisionFileField(storage=django.core.files.storage.FileSystemStorage(base_url='/private/', location='/home/thibault/code/phase/private'), upload_to=documents.fileutils.revision_file_path, null=True, verbose_name='PDF File', blank=True)),
                ('received_date', models.DateField(verbose_name='Received date')),
                ('created_on', models.DateField(default=django.utils.timezone.now, verbose_name='Created on')),
                ('updated_on', models.DateTimeField(auto_now=True, verbose_name='Updated on')),
                ('status', metadata.fields.ConfigurableChoiceField(max_length=20, verbose_name='Status', list_index=b'STATUS_COR_MOM')),
            ],
            options={
                'ordering': ('-revision',),
                'abstract': False,
                'get_latest_by': 'revision',
            },
        ),
    ]
