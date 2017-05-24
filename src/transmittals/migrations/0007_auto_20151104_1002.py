# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0006_auto_20151102_1511'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='outgoingtransmittalrevision',
            options={},
        ),
        migrations.AlterModelOptions(
            name='transmittalrevision',
            options={},
        ),
        migrations.AlterUniqueTogether(
            name='outgoingtransmittalrevision',
            unique_together=set([]),
        ),
        migrations.AlterUniqueTogether(
            name='transmittalrevision',
            unique_together=set([]),
        ),
    ]
