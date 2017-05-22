# -*- coding: utf-8 -*-


from django.db import migrations, models


def copy_contracts_numbers(apps, schema_editor):
    TrsRevision = apps.get_model('transmittals', 'TrsRevision')
    for otg in TrsRevision.objects.all():
        otg.contract_number_new = otg.contract_number
        otg.save()


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0032_auto_20160203_1040'),
    ]

    operations = [
        migrations.RunPython(copy_contracts_numbers),
    ]
