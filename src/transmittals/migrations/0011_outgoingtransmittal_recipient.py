# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20151125_1117'),
        ('transmittals', '0010_remove_outgoingtransmittal_recipient'),
    ]

    operations = [
        migrations.AddField(
            model_name='outgoingtransmittal',
            name='recipient',
            field=models.ForeignKey(default=1, verbose_name='Recipient', to='accounts.Entity'),
            preserve_default=False,
        ),
    ]
