# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0016_exportedrevision_comments'),
        ('default_documents', '0017_contractordeliverablerevision_under_preparation_by'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contractordeliverablerevision',
            name='already_transmitted',
        ),
        migrations.AddField(
            model_name='contractordeliverablerevision',
            name='transmittal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='transmittal', blank=True, to='transmittals.OutgoingTransmittal', null=True),
        ),
        migrations.AddField(
            model_name='contractordeliverablerevision',
            name='transmittal_sent_date',
            field=models.DateField(null=True, verbose_name='Transmittal sent date', blank=True),
        ),
    ]
