# -*- coding: utf-8 -*-


from django.db import migrations


def copy_contracts_from_values_list(apps, schema_editor):
    ValuesList = apps.get_model("metadata", "ValuesList")
    Contract = apps.get_model("categories", "Contract")
    try:
        value_list = ValuesList.objects.filter(index='CONTRACT_NBS').get()
    except ValuesList.DoesNotExist:
        return

    for contract in value_list.values.all():
        Contract.objects.create(number=contract.index, name=contract.value)


class Migration(migrations.Migration):

    dependencies = [
        ('metadata', '0002_return_code_values'),
        ('categories', '0009_contract'),
    ]

    operations = [
        migrations.RunPython(copy_contracts_from_values_list)
    ]
