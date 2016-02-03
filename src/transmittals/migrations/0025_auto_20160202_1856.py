# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import metadata.fields


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0024_auto_20160202_1838'),
    ]

    operations = [
        migrations.AlterField(
            model_name='outgoingtransmittal',
            name='contract_number_old',
            field=metadata.fields.ConfigurableChoiceField(max_length=8, null=True, verbose_name='Contract Number', list_index='CONTRACT_NBS', blank=True),
        ),
    ]
