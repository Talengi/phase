# -*- coding: utf-8 -*-


from django.db import migrations


def create_return_codes(apps, schema_editor):
    ValuesList = apps.get_model('metadata', 'ValuesList')
    ListEntry = apps.get_model('metadata', 'ListEntry')

    vlist = ValuesList.objects.create(
        index='REVIEW_RETURN_CODES',
        name='Review return codes')

    ListEntry.objects.create(
        values_list=vlist,
        order=0,
        index='0',
        value='Not returned by CA on time')
    ListEntry.objects.create(
        values_list=vlist,
        order=1,
        index='1',
        value='Approved / Reviewed without comments')
    ListEntry.objects.create(
        values_list=vlist,
        order=2,
        index='2',
        value='Approved / Reviewed with comments')
    ListEntry.objects.create(
        values_list=vlist,
        order=3,
        index='3',
        value='Rejected')
    ListEntry.objects.create(
        values_list=vlist,
        order=4,
        index='4',
        value='No further comments on this revision')


class Migration(migrations.Migration):

    dependencies = [
        ('metadata', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_return_codes),
    ]
