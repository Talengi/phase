# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def copy_contracts_numbers(apps, schema_editor):
    Transmittal = apps.get_model('transmittals', 'Transmittal')
    for otg in Transmittal.objects.all():
        otg.contract_number = otg.contract_number_old
        otg.save()


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0031_trsrevision_contract_number_new'),
    ]

    operations = [
        migrations.RunPython(copy_contracts_numbers)
    ]

