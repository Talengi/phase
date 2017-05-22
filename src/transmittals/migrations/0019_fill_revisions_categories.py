# -*- coding: utf-8 -*-


from django.db import migrations


def fill_revisions_categories(apps, schema_editor):
    ExportedRevision = apps.get_model('transmittals', 'ExportedRevision')
    revs = ExportedRevision.objects.select_related()

    for rev in revs:
        trs = rev.transmittal
        if trs.revisions_category:
            continue

        category = rev.document.category
        trs.revisions_category = category
        trs.save()


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0018_outgoingtransmittal_revisions_category'),
    ]

    operations = [
        migrations.RunPython(fill_revisions_categories)
    ]
