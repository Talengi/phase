# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0013_auto_20151202_1413'),
    ]

    operations = [
        migrations.AddField(
            model_name='outgoingtransmittal',
            name='document_number',
            field=models.CharField(max_length=250, null=True, verbose_name='Document number'),
        ),
        migrations.AddField(
            model_name='transmittal',
            name='document_number',
            field=models.CharField(max_length=250, null=True, verbose_name='Document number'),
        ),
        migrations.AlterField(
            model_name='outgoingtransmittal',
            name='document_key',
            field=models.SlugField(unique=True, max_length=250, verbose_name='Document key'),
        ),
        migrations.AlterField(
            model_name='transmittal',
            name='document_key',
            field=models.SlugField(unique=True, max_length=250, verbose_name='Document key'),
        ),
    ]
