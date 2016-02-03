# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0039_auto_20160203_1242'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='minutesofmeeting',
            unique_together=set([('contract_number_new', 'originator', 'recipient', 'document_type', 'sequential_number')]),
        ),
    ]
