# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0050_auto_20160224_1147'),
        ('documents', '0007_set_metadata_value'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contractordeliverablerevision',
            name='metadata',
            field=models.ForeignKey(to='default_documents.ContractorDeliverable'),
        ),
        migrations.AlterField(
            model_name='correspondencerevision',
            name='metadata',
            field=models.ForeignKey(to='default_documents.Correspondence'),
        ),
        migrations.AlterField(
            model_name='demometadatarevision',
            name='metadata',
            field=models.ForeignKey(to='default_documents.DemoMetadata'),
        ),
        migrations.AlterField(
            model_name='minutesofmeetingrevision',
            name='metadata',
            field=models.ForeignKey(to='default_documents.MinutesOfMeeting'),
        ),
    ]
