# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0056_auto_20160225_1526'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='contractordeliverable',
            unique_together=set([('contract_number', 'originator_new', 'unit', 'discipline', 'document_type', 'sequential_number')]),
        ),
    ]
