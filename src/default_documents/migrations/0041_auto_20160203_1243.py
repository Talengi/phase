# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0040_auto_20160203_1243'),
    ]

    operations = [
        migrations.RenameField(
            model_name='minutesofmeeting',
            old_name='contract_number',
            new_name='contract_number_old',
        ),
    ]
