# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0046_auto_20160224_1214'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='outgoingtransmittalrevision',
            name='document',
        ),
        migrations.RemoveField(
            model_name='transmittalrevision',
            name='document',
        ),
    ]
