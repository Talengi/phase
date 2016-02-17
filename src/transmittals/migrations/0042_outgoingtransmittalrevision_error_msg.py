# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0041_outgoingtransmittal_ack_of_receipt_author'),
    ]

    operations = [
        migrations.AddField(
            model_name='outgoingtransmittalrevision',
            name='error_msg',
            field=models.TextField(help_text='Report an error to the DC', null=True, verbose_name='Error message', blank=True),
        ),
    ]
