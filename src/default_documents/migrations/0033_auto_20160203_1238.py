# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0032_auto_20160203_1238'),
    ]

    operations = [
        migrations.RenameField(
            model_name='correspondence',
            old_name='contract_number',
            new_name='contract_number_old',
        ),
    ]
