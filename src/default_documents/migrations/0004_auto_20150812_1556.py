# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0003_auto_20150812_1036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contractordeliverablerevision',
            name='reviewers_step_closed',
            field=models.DateField(null=True, verbose_name='Reviewers step closed', blank=True),
        ),
        migrations.AlterField(
            model_name='demometadatarevision',
            name='reviewers_step_closed',
            field=models.DateField(null=True, verbose_name='Reviewers step closed', blank=True),
        ),
    ]
