# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from documents.utils import get_all_revision_classes


def set_metadata_values(*args):
    classes = get_all_revision_classes()
    for class_ in classes:
        revisions = class_.objects.all()
        for revision in revisions:
            revision.metadata = revision.document.get_metadata()
            revision.save()


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0006_create_protected_dir'),
    ]

    operations = [
        migrations.RunPython(set_metadata_values)
    ]
