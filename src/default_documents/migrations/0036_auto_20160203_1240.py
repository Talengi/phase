# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0035_auto_20160203_1239'),
    ]

    operations = [
        migrations.RenameField(
            model_name='correspondence',
            old_name='contract_number_new',
            new_name='contract_number',
        ),
    ]
