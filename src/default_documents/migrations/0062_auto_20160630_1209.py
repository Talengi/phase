# -*- coding: utf-8 -*-


from django.db import migrations, models
import metadata.fields
import django.utils.timezone
import documents.fileutils
import documents.fields
import transmittals.fileutils
import privatemedia.fields
import privatemedia.storage
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0055_auto_20160303_1439'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('documents', '0008_auto_20160607_1650'),
        ('accounts', '0009_auto_20160322_1156'),
        ('default_documents', '0061_auto_20160322_1222'),
    ]

    operations = [
        migrations.CreateModel(
            name='GtgMetadata',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('document_key', models.SlugField(unique=True, max_length=250, verbose_name='Document key', blank=True)),
                ('document_number', models.CharField(max_length=250, verbose_name='Document number', blank=True)),
                ('title', models.TextField(verbose_name='title')),
                ('unit', metadata.fields.ConfigurableChoiceField(default='000', max_length=3, verbose_name='Unit', list_index='GTG_UNITS')),
                ('discipline', metadata.fields.ConfigurableChoiceField(max_length=6, null=True, verbose_name='Discipline', list_index='GTG_DISCIPLINES', blank=True)),
                ('document_type', metadata.fields.ConfigurableChoiceField(max_length=3, verbose_name='Document Type', list_index='GTG_DOCUMENT_TYPES')),
                ('status_ifr_planned_date', models.DateField(null=True, verbose_name='Status IFR Planned Date', blank=True)),
                ('status_ifr_forecast_date', models.DateField(null=True, verbose_name='Status IFR Forecast Date', blank=True)),
                ('status_ifr_actual_date', models.DateField(null=True, verbose_name='Status IFR Actual Date', blank=True)),
                ('status_ifa_planned_date', models.DateField(null=True, verbose_name='Status IFA Planned Date', blank=True)),
                ('status_ifa_forecast_date', models.DateField(null=True, verbose_name='Status IFA Forecast Date', blank=True)),
                ('status_ifa_actual_date', models.DateField(null=True, verbose_name='Status IFA Actual Date', blank=True)),
                ('status_ifi_planned_date', models.DateField(null=True, verbose_name='Status IFI Planned Date', blank=True)),
                ('status_ifi_forecast_date', models.DateField(null=True, verbose_name='Status IFI Forecast Date', blank=True)),
                ('status_ifi_actual_date', models.DateField(null=True, verbose_name='Status IFI Actual Date', blank=True)),
                ('status_ife_planned_date', models.DateField(null=True, verbose_name='Status IFE Planned Date', blank=True)),
                ('status_ife_forecast_date', models.DateField(null=True, verbose_name='Status IFE Forecast Date', blank=True)),
                ('status_ife_actual_date', models.DateField(null=True, verbose_name='Status IFE Actual Date', blank=True)),
                ('status_ifp_planned_date', models.DateField(null=True, verbose_name='Status IFP Planned Date', blank=True)),
                ('status_ifp_forecast_date', models.DateField(null=True, verbose_name='Status IFP Forecast Date', blank=True)),
                ('status_ifp_actual_date', models.DateField(null=True, verbose_name='Status IFP Actual Date', blank=True)),
                ('status_fin_planned_date', models.DateField(null=True, verbose_name='Status FIN Planned Date', blank=True)),
                ('status_fin_forecast_date', models.DateField(null=True, verbose_name='Status FIN Forecast Date', blank=True)),
                ('status_fin_actual_date', models.DateField(null=True, verbose_name='Status FIN Actual Date', blank=True)),
                ('status_asb_planned_date', models.DateField(null=True, verbose_name='Status ASB Planned Date', blank=True)),
                ('status_asb_forecast_date', models.DateField(null=True, verbose_name='Status ASB Forecast Date', blank=True)),
                ('status_asb_actual_date', models.DateField(null=True, verbose_name='Status ASB Actual Date', blank=True)),
                ('document', models.OneToOneField(to='documents.Document')),
            ],
            options={
                'ordering': ('document_number',),
                'verbose_name': 'Gtg deliverable',
                'verbose_name_plural': 'Gtg deliverables',
            },
        ),
        migrations.CreateModel(
            name='GtgMetadataRevision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('revision', models.PositiveIntegerField(verbose_name='Revision')),
                ('revision_date', models.DateField(null=True, verbose_name='Revision Date', blank=True)),
                ('native_file', documents.fields.RevisionFileField(upload_to=documents.fileutils.revision_file_path, storage=privatemedia.storage.ProtectedStorage(), max_length=255, blank=True, null=True, verbose_name='Native File')),
                ('pdf_file', documents.fields.RevisionFileField(storage=privatemedia.storage.ProtectedStorage(), upload_to=documents.fileutils.revision_file_path, null=True, verbose_name='PDF File', blank=True)),
                ('created_on', models.DateField(default=django.utils.timezone.now, verbose_name='Created on')),
                ('updated_on', models.DateTimeField(auto_now=True, verbose_name='Updated on')),
                ('received_date', models.DateField(verbose_name='Received date')),
                ('review_start_date', models.DateField(null=True, verbose_name='Review start date', blank=True)),
                ('review_due_date', models.DateField(null=True, verbose_name='Review due date', blank=True)),
                ('reviewers_step_closed', models.DateField(null=True, verbose_name='Reviewers step closed', blank=True)),
                ('leader_step_closed', models.DateField(null=True, verbose_name='Leader step closed', blank=True)),
                ('review_end_date', models.DateField(null=True, verbose_name='Review end date', blank=True)),
                ('docclass', models.IntegerField(default=1, verbose_name='Class', choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4')])),
                ('return_code', metadata.fields.ConfigurableChoiceField(max_length=3, null=True, verbose_name='Return code', list_index='REVIEW_RETURN_CODES', blank=True)),
                ('transmittal_sent_date', models.DateField(null=True, verbose_name='Transmittal sent date', blank=True)),
                ('trs_return_code', metadata.fields.ConfigurableChoiceField(max_length=3, null=True, verbose_name='Final return code', list_index='REVIEW_RETURN_CODES', blank=True)),
                ('file_transmitted', privatemedia.fields.PrivateFileField(storage=privatemedia.storage.ProtectedStorage(), upload_to=transmittals.fileutils.file_transmitted_file_path, null=True, verbose_name='File Transmitted', blank=True)),
                ('internal_review', models.BooleanField(default=False, verbose_name='Internal review only?', choices=[(False, 'No'), (True, 'Yes')])),
                ('purpose_of_issue', models.CharField(default='FR', max_length=2, verbose_name='Purpose of issue', blank=True, choices=[('FR', 'For review'), ('FI', 'For information')])),
                ('external_review_due_date', models.DateField(null=True, verbose_name='External due date', blank=True)),
                ('status', metadata.fields.ConfigurableChoiceField(max_length=3, null=True, verbose_name='Status', list_index='GTG_STATUSES', blank=True)),
                ('final_revision', models.NullBooleanField(verbose_name='Is final revision?', choices=[(True, 'Yes'), (False, 'No')])),
                ('approver', models.ForeignKey(related_name='default_documents_gtgmetadatarevision_related_approver', verbose_name='Approver', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('leader', models.ForeignKey(related_name='default_documents_gtgmetadatarevision_related_leader', verbose_name='Leader', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('metadata', models.ForeignKey(to='default_documents.GtgMetadata')),
                ('reviewers', models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='Reviewers', blank=True)),
                ('transmittal', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='transmittal', blank=True, to='transmittals.OutgoingTransmittal', null=True)),
                ('transmittals', models.ManyToManyField(related_name='default_documents_gtgmetadatarevision_related', verbose_name='transmittals', to='transmittals.OutgoingTransmittal')),
                ('under_preparation_by', models.ForeignKey(related_name='+', verbose_name='Under preparation by', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='gtgmetadata',
            name='latest_revision',
            field=models.ForeignKey(verbose_name='Latest revision', to='default_documents.GtgMetadataRevision', null=True),
        ),
        migrations.AddField(
            model_name='gtgmetadata',
            name='originator',
            field=models.ForeignKey(verbose_name='Originator', to='accounts.Entity'),
        ),
        migrations.AddField(
            model_name='gtgmetadata',
            name='related_documents',
            field=models.ManyToManyField(related_name='gtg_related_documents', to='documents.Document', blank=True),
        ),
    ]
