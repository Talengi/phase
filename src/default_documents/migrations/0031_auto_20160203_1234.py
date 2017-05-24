# -*- coding: utf-8 -*-


from django.db import migrations, models


def copy_contracts_numbers(apps, schema_editor):
    Correspondence = apps.get_model('default_documents', 'Correspondence')
    for corresp in Correspondence.objects.all():
        corresp.contract_number_new = corresp.contract_number
        corresp.save()
        

class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0030_correspondence_contract_number_new'),
    ]

    operations = [
        migrations.RunPython(copy_contracts_numbers)
    ]
