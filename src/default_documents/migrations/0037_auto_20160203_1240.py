# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0036_auto_20160203_1240'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='correspondence',
            unique_together=set([('contract_number', 'originator', 'recipient', 'document_type', 'sequential_number')]),
        ),
    ]
