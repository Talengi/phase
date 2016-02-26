# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0058_remove_contractordeliverable_originator'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contractordeliverable',
            old_name='originator_new',
            new_name='originator',
        ),
        migrations.AlterUniqueTogether(
            name='contractordeliverable',
            unique_together=set([('contract_number', 'originator', 'unit', 'discipline', 'document_type', 'sequential_number')]),
        ),
    ]
