# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import privatemedia.fields
import privatemedia.storage


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0048_auto_20160224_1526'),
    ]

    operations = [
        migrations.AddField(
            model_name='outgoingtransmittal',
            name='archived_pdf',
            field=privatemedia.fields.PrivateFileField(storage=privatemedia.storage.ProtectedStorage(), upload_to=b'', null=True, verbose_name='Archived PDF', blank=True),
        ),
    ]
