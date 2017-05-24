# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0028_auto_20160203_1221'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='contractordeliverable',
            unique_together=set([('contract_number', 'originator', 'unit', 'discipline', 'document_type', 'sequential_number')]),
        ),
    ]
