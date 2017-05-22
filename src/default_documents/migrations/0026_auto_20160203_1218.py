# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0025_auto_20160203_1218'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contractordeliverable',
            old_name='contract_number',
            new_name='contract_number_old',
        ),
    ]
