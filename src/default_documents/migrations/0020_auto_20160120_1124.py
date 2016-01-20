# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0019_contractordeliverablerevision_internal_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='contractordeliverablerevision',
            name='external_review_due_date',
            field=models.DateField(null=True, verbose_name='External due date', blank=True),
        ),
        migrations.AddField(
            model_name='contractordeliverablerevision',
            name='purpose_of_issue',
            field=models.CharField(default='FI', max_length=2, verbose_name='Outgoing trs purpose of issue', choices=[('FR', 'For review'), ('FI', 'For information')]),
        ),
        migrations.AlterField(
            model_name='contractordeliverablerevision',
            name='internal_review',
            field=models.BooleanField(default=False, verbose_name='Internal review only?', choices=[(False, 'No'), (True, 'Yes')]),
        ),
    ]
