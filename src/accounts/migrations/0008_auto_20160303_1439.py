# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_auto_20160225_1510'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='send_closed_reviews_mails',
            field=models.BooleanField(default=True, verbose_name='Send mails when reviews are closed'),
        ),
        migrations.AddField(
            model_name='user',
            name='send_pending_reviews_mails',
            field=models.BooleanField(default=True, verbose_name='Send pending reviews reminders'),
        ),
        migrations.AddField(
            model_name='user',
            name='send_trs_reminders_mails',
            field=models.BooleanField(default=True, verbose_name='Send reminders for trs with missing ack of receipt'),
        ),
    ]
