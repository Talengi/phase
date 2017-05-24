# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0027_auto_20160203_1220'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contractordeliverable',
            old_name='contract_number_new',
            new_name='contract_number',
        ),
    ]
