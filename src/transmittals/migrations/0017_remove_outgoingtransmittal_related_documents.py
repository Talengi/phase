# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0016_exportedrevision_comments'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='outgoingtransmittal',
            name='related_documents',
        ),
    ]
