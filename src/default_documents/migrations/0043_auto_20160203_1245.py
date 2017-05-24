# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0042_auto_20160203_1244'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='minutesofmeeting',
            unique_together=set([('contract_number_old', 'originator', 'recipient', 'document_type', 'sequential_number')]),
        ),
    ]
