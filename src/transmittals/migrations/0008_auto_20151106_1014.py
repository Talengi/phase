# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0007_auto_20151104_1002'),
    ]

    operations = [
        migrations.AlterField(
            model_name='outgoingtransmittal',
            name='originator',
            field=models.CharField(max_length=3, verbose_name='Originator'),
        ),
        migrations.AlterField(
            model_name='outgoingtransmittal',
            name='recipient',
            field=models.CharField(max_length=3, verbose_name='Recipient'),
        ),
    ]
