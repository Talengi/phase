# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def make_entities(apps, schema):
    TrsRevision = apps.get_model(
        'transmittals', 'TrsRevision')
    Entity = apps.get_model('accounts', 'Entity')
    revisions = TrsRevision.objects.all()
    for rev in revisions:
        entity, created = Entity.objects.get_or_create(
            trigram=rev.originator,
            defaults={
                'type': 'originator',
                'name': rev.originator
            }
        )
        if created:
            print('New entity created: {}'.format(entity.name))

        rev.originator_new = entity
        rev.save()


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0049_trsrevision_originator_new'),
    ]

    operations = [
        migrations.RunPython(make_entities)
    ]
