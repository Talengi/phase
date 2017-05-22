# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0051_auto_20160224_1214'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contractordeliverablerevision',
            name='document',
        ),
        migrations.RemoveField(
            model_name='correspondencerevision',
            name='document',
        ),
        migrations.RemoveField(
            model_name='demometadatarevision',
            name='document',
        ),
        migrations.RemoveField(
            model_name='minutesofmeetingrevision',
            name='document',
        ),
    ]
