# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0015_auto_20151211_1055'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='correspondencerevision',
            options={},
        ),
        migrations.AlterModelOptions(
            name='minutesofmeetingrevision',
            options={},
        ),
        migrations.AlterUniqueTogether(
            name='correspondencerevision',
            unique_together=set([]),
        ),
        migrations.AlterUniqueTogether(
            name='minutesofmeetingrevision',
            unique_together=set([]),
        ),
    ]
