# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0008_auto_20151015_1453'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contractordeliverablerevision',
            old_name='dc_return_code',
            new_name='trs_return_code',
        ),
        migrations.RemoveField(
            model_name='contractordeliverablerevision',
            name='dc_comments',
        ),
        migrations.RemoveField(
            model_name='demometadatarevision',
            name='dc_comments',
        ),
        migrations.RemoveField(
            model_name='demometadatarevision',
            name='dc_return_code',
        ),
        migrations.AddField(
            model_name='contractordeliverablerevision',
            name='already_transmitted',
            field=models.BooleanField(default=False, verbose_name='Already embdedded in transmittal?'),
        ),
    ]
