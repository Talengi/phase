# -*- coding: utf-8 -*-


from django.db import migrations, models


def copy_contracts_numbers(apps, schema_editor):
    MinutesOfMeeting = apps.get_model('default_documents', 'MinutesOfMeeting')
    for mom in MinutesOfMeeting.objects.all():
        mom.contract_number_new = mom.contract_number
        mom.save()


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0038_minutesofmeeting_contract_number_new'),
    ]

    operations = [
        migrations.RunPython(copy_contracts_numbers)
    ]
