# -*- coding: utf-8 -*-


from django.db import migrations, models


def copy_contracts_numbers(apps, schema_editor):
    ContractorDeliverable = apps.get_model('default_documents', 'ContractorDeliverable')
    for ctd in ContractorDeliverable.objects.all():
        ctd.contract_number_new = ctd.contract_number
        ctd.save()


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0023_contractordeliverable_contract_number_new'),
    ]

    operations = [
        migrations.RunPython(copy_contracts_numbers),
    ]
