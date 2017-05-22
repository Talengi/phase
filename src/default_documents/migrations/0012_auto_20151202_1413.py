# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0011_auto_20151126_1707'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contractordeliverablerevision',
            name='revision',
            field=models.PositiveIntegerField(verbose_name='Revision'),
        ),
        migrations.AlterField(
            model_name='correspondencerevision',
            name='revision',
            field=models.PositiveIntegerField(verbose_name='Revision'),
        ),
        migrations.AlterField(
            model_name='demometadatarevision',
            name='revision',
            field=models.PositiveIntegerField(verbose_name='Revision'),
        ),
        migrations.AlterField(
            model_name='minutesofmeetingrevision',
            name='revision',
            field=models.PositiveIntegerField(verbose_name='Revision'),
        ),
    ]
