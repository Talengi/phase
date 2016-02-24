# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0049_auto_20160215_1503'),
    ]

    operations = [
        migrations.AddField(
            model_name='contractordeliverablerevision',
            name='metadata',
            field=models.ForeignKey(blank=True, to='default_documents.ContractorDeliverable', null=True),
        ),
        migrations.AddField(
            model_name='correspondencerevision',
            name='metadata',
            field=models.ForeignKey(blank=True, to='default_documents.Correspondence', null=True),
        ),
        migrations.AddField(
            model_name='demometadatarevision',
            name='metadata',
            field=models.ForeignKey(blank=True, to='default_documents.DemoMetadata', null=True),
        ),
        migrations.AddField(
            model_name='minutesofmeetingrevision',
            name='metadata',
            field=models.ForeignKey(blank=True, to='default_documents.MinutesOfMeeting', null=True),
        ),
    ]
