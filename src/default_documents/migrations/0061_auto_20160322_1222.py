# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def copy_transmittal_to_transmittals(apps, schema_editor):
    ContractorDeliverableRevision = apps.get_model(
        'default_documents', 'ContractorDeliverableRevision')
    for rev in ContractorDeliverableRevision.objects.filter(transmittal__isnull=False):
        rev.transmittals.add(rev.transmittal)
        rev.save()


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0060_contractordeliverablerevision_transmittals'),
    ]

    operations = [
        migrations.RunPython(copy_transmittal_to_transmittals),
    ]

