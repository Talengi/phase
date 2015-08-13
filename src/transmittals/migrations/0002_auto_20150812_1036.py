# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import default_documents.validators


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trsrevision',
            name='sequential_number',
            field=models.CharField(default='0001', validators=[default_documents.validators.StringNumberValidator(length=4)], max_length=4, blank=True, help_text='Select a four digit number', null=True, verbose_name='sequential Number'),
        ),
    ]
