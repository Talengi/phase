# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0018_auto_20160111_1400'),
    ]

    operations = [
        migrations.AddField(
            model_name='contractordeliverablerevision',
            name='internal_review',
            field=models.BooleanField(default=False, verbose_name='Internal review only?'),
        ),
    ]
