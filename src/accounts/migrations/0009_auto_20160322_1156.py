# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_auto_20160303_1439'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='send_trs_reminders_mails',
            field=models.BooleanField(default=True, verbose_name='Send reminders for outgoing transmittals with missing acknowledgement of receipt'),
        ),
    ]
