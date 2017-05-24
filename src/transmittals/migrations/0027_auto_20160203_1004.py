# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0026_transmittal_contract_number_new'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='transmittal',
            index_together=set([('originator', 'recipient', 'sequential_number', 'status')]),
        ),
    ]
