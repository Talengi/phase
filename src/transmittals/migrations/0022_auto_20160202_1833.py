# -*- coding: utf-8 -*-


from django.db import migrations, models


def copy_contracts_numbers(apps, schema_editor):
    OutgoingTransmittal = apps.get_model('transmittals', 'OutgoingTransmittal')
    for otg in OutgoingTransmittal.objects.all():
        otg.contract_number_new = otg.contract_number
        otg.save()


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0021_outgoingtransmittal_contract_number_new'),
    ]

    operations = [
        migrations.RunPython(copy_contracts_numbers),
    ]
