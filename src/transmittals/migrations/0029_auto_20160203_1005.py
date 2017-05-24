# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0028_auto_20160203_1004'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transmittal',
            old_name='contract_number_new',
            new_name='contract_number',
        ),
    ]
