# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('default_documents', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='minutesofmeetingrevision',
            name='document',
            field=models.ForeignKey(to='documents.Document'),
        ),
        migrations.AddField(
            model_name='minutesofmeeting',
            name='document',
            field=models.OneToOneField(to='documents.Document'),
        ),
        migrations.AddField(
            model_name='minutesofmeeting',
            name='latest_revision',
            field=models.ForeignKey(verbose_name='Latest revision', to='default_documents.MinutesOfMeetingRevision'),
        ),
        migrations.AddField(
            model_name='minutesofmeeting',
            name='response_reference',
            field=models.ManyToManyField(related_name='mom_correspondence_related_set', to='default_documents.Correspondence', blank=True),
        ),
        migrations.AddField(
            model_name='demometadatarevision',
            name='approver',
            field=models.ForeignKey(related_name='default_documents_demometadatarevision_related_approver', verbose_name='Approver', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='demometadatarevision',
            name='document',
            field=models.ForeignKey(to='documents.Document'),
        ),
        migrations.AddField(
            model_name='demometadatarevision',
            name='leader',
            field=models.ForeignKey(related_name='default_documents_demometadatarevision_related_leader', verbose_name='Leader', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='demometadatarevision',
            name='reviewers',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='Reviewers', blank=True),
        ),
        migrations.AddField(
            model_name='demometadata',
            name='document',
            field=models.OneToOneField(to='documents.Document'),
        ),
        migrations.AddField(
            model_name='demometadata',
            name='latest_revision',
            field=models.ForeignKey(verbose_name='Latest revision', to='default_documents.DemoMetadataRevision', null=True),
        ),
        migrations.AddField(
            model_name='demometadata',
            name='related_documents',
            field=models.ManyToManyField(related_name='demometadata_related_set', to='documents.Document', blank=True),
        ),
        migrations.AddField(
            model_name='correspondencerevision',
            name='document',
            field=models.ForeignKey(to='documents.Document'),
        ),
        migrations.AddField(
            model_name='correspondencerevision',
            name='leader',
            field=models.ForeignKey(related_name='leading_correspondance', verbose_name='Leader', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='correspondence',
            name='document',
            field=models.OneToOneField(to='documents.Document'),
        ),
        migrations.AddField(
            model_name='correspondence',
            name='latest_revision',
            field=models.ForeignKey(verbose_name='Latest revision', to='default_documents.CorrespondenceRevision'),
        ),
        migrations.AddField(
            model_name='correspondence',
            name='related_documents',
            field=models.ManyToManyField(related_name='correspondence_related_set', to='documents.Document', blank=True),
        ),
        migrations.AddField(
            model_name='contractordeliverablerevision',
            name='approver',
            field=models.ForeignKey(related_name='default_documents_contractordeliverablerevision_related_approver', verbose_name='Approver', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='contractordeliverablerevision',
            name='document',
            field=models.ForeignKey(to='documents.Document'),
        ),
        migrations.AddField(
            model_name='contractordeliverablerevision',
            name='leader',
            field=models.ForeignKey(related_name='default_documents_contractordeliverablerevision_related_leader', verbose_name='Leader', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='contractordeliverablerevision',
            name='reviewers',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='Reviewers', blank=True),
        ),
        migrations.AddField(
            model_name='contractordeliverable',
            name='document',
            field=models.OneToOneField(to='documents.Document'),
        ),
        migrations.AddField(
            model_name='contractordeliverable',
            name='latest_revision',
            field=models.ForeignKey(verbose_name='Latest revision', to='default_documents.ContractorDeliverableRevision'),
        ),
        migrations.AddField(
            model_name='contractordeliverable',
            name='related_documents',
            field=models.ManyToManyField(related_name='cd_related_documents', to='documents.Document', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='minutesofmeetingrevision',
            unique_together=set([('document', 'revision')]),
        ),
        migrations.AlterUniqueTogether(
            name='minutesofmeeting',
            unique_together=set([('contract_number', 'originator', 'recipient', 'document_type', 'sequential_number')]),
        ),
        migrations.AlterUniqueTogether(
            name='correspondencerevision',
            unique_together=set([('document', 'revision')]),
        ),
        migrations.AlterUniqueTogether(
            name='correspondence',
            unique_together=set([('contract_number', 'originator', 'recipient', 'document_type', 'sequential_number')]),
        ),
        migrations.AlterUniqueTogether(
            name='contractordeliverable',
            unique_together=set([('contract_number', 'originator', 'unit', 'discipline', 'document_type', 'sequential_number')]),
        ),
    ]
