# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0011_outgoingtransmittal_recipient'),
    ]

    operations = [
        migrations.AddField(
            model_name='outgoingtransmittal',
            name='ack_of_receipt_date',
            field=models.DateField(null=True, verbose_name='Acknowledgment of receipt date', blank=True),
        ),
    ]
