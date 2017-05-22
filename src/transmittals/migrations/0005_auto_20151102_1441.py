# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0004_auto_20151102_1437'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='outgoingtransmittal',
            options={'ordering': ('document_key',), 'verbose_name': 'Outgoing transmittal', 'verbose_name_plural': 'Outgoing transmittals'},
        ),
        migrations.RenameField(
            model_name='outgoingtransmittal',
            old_name='related_revisions',
            new_name='related_documents',
        ),
    ]
