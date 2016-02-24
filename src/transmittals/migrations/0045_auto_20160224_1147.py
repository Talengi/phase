# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0044_remove_outgoingtransmittalrevision_received_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='outgoingtransmittalrevision',
            name='metadata',
            field=models.ForeignKey(blank=True, to='transmittals.OutgoingTransmittal', null=True),
        ),
        migrations.AddField(
            model_name='transmittalrevision',
            name='metadata',
            field=models.ForeignKey(blank=True, to='transmittals.Transmittal', null=True),
        ),
    ]
