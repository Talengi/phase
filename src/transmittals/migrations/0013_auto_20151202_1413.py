# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0012_outgoingtransmittal_ack_of_receipt_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='outgoingtransmittalrevision',
            name='revision',
            field=models.PositiveIntegerField(verbose_name='Revision'),
        ),
        migrations.AlterField(
            model_name='transmittalrevision',
            name='revision',
            field=models.PositiveIntegerField(verbose_name='Revision'),
        ),
    ]
