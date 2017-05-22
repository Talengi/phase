# -*- coding: utf-8 -*-


from django.db import models, migrations
import privatemedia.fields
import django.core.files.storage


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0015_auto_20151211_1055'),
    ]

    operations = [
        migrations.AddField(
            model_name='exportedrevision',
            name='comments',
            field=privatemedia.fields.PrivateFileField(storage=django.core.files.storage.FileSystemStorage(base_url='/private/', location='/home/thibault/code/phase/private'), upload_to=b'', null=True, verbose_name='Comments', blank=True),
        ),
    ]
