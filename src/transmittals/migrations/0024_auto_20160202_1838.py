# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0023_auto_20160202_1837'),
    ]

    operations = [
        migrations.RenameField(
            model_name='outgoingtransmittal',
            old_name='contract_number_new',
            new_name='contract_number',
        ),
    ]
