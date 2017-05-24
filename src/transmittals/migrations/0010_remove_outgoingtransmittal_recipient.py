# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0009_auto_20151117_1535'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='outgoingtransmittal',
            name='recipient',
        ),
    ]
