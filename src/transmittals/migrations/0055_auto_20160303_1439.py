# -*- coding: utf-8 -*-


from django.db import migrations, models
import transmittals.fields
import privatemedia.storage


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0054_outgoingtransmittal_archived_pdf'),
    ]

    operations = [
        migrations.AlterField(
            model_name='outgoingtransmittal',
            name='archived_pdf',
            field=transmittals.fields.OgtFileField(storage=privatemedia.storage.ProtectedStorage(), upload_to=transmittals.fields.ogt_file_path, null=True, verbose_name='Archived PDF', blank=True),
        ),
    ]
