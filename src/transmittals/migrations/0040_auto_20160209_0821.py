# -*- coding: utf-8 -*-


from django.db import migrations, models
import privatemedia.fileutils
import privatemedia.fields


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0039_auto_20160203_1150'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exportedrevision',
            name='comments',
            field=privatemedia.fields.ProtectedFileField(storage=privatemedia.fileutils.ProtectedStorage(), upload_to=b'', null=True, verbose_name='Comments', blank=True),
        ),
    ]
