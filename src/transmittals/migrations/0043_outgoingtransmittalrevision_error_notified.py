# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0042_outgoingtransmittalrevision_error_msg'),
    ]

    operations = [
        migrations.AddField(
            model_name='outgoingtransmittalrevision',
            name='error_notified',
            field=models.BooleanField(default=False, verbose_name='Was error already notified?'),
        ),
    ]
