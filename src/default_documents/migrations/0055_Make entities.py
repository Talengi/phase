# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def make_entities(apps, schema):
    ContractorDeliverable = apps.get_model(
        'default_documents', 'ContractorDeliverable')
    Entity = apps.get_model('accounts', 'Entity')
    deliverables = ContractorDeliverable.objects.all()
    for deliverable in deliverables:
        entity, created = Entity.objects.get_or_create(
            trigram=deliverable.originator,
            defaults={
                'type': 'originator',
                'name': deliverable.originator
            }
        )
        if created:
            print 'New entity created: {}'.format(entity.name)

        deliverable.originator_new = entity
        deliverable.save()


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0054_contractordeliverable_originator_new'),
    ]

    operations = [
        migrations.RunPython(make_entities)
    ]
