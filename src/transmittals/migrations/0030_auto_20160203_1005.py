# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0029_auto_20160203_1005'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='transmittal',
            index_together=set([('contract_number', 'originator', 'recipient', 'sequential_number', 'status')]),
        ),
    ]
