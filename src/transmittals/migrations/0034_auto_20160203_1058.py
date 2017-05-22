# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0033_auto_20160203_1055'),
    ]

    operations = [
        migrations.RenameField(
            model_name='trsrevision',
            old_name='contract_number',
            new_name='contract_number_old',
        ),
    ]
