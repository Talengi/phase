# -*- coding: utf-8 -*-


from django.db import migrations, models
import privatemedia.fileutils
import privatemedia.fields
import transmittals.fileutils


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0045_auto_20160203_1245'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contractordeliverablerevision',
            name='trs_comments',
            field=privatemedia.fields.ProtectedFileField(storage=privatemedia.fileutils.ProtectedStorage(), upload_to=transmittals.fileutils.trs_comments_file_path, null=True, verbose_name='File Transmitted', blank=True),
        ),
    ]
