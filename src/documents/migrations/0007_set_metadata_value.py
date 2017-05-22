# -*- coding: utf-8 -*-


from django.db import migrations
from documents.utils import get_all_revision_types


def set_metadata_values(apps, schema_editor):
    types = get_all_revision_types()
    for type_ in types:
        class_ = apps.get_model(type_.app_label, type_.model_class().__name__)
        revisions = class_.objects.all()
        for revision in revisions:
            revision.metadata = revision.document.get_metadata()
            revision.save()


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0006_create_protected_dir'),
        ('default_documents', '0050_auto_20160224_1147'),
        ('transmittals', '0045_auto_20160224_1147'),
    ]

    operations = [
        migrations.RunPython(set_metadata_values)
    ]
