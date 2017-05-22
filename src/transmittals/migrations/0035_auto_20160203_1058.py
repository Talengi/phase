# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0034_auto_20160203_1058'),
    ]

    operations = [
        migrations.RenameField(
            model_name='trsrevision',
            old_name='contract_number_new',
            new_name='contract_number',
        ),
    ]
