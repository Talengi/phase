# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0014_auto_20151210_1121'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='outgoingtransmittal',
            options={'ordering': ('document_number',), 'verbose_name': 'Outgoing transmittal', 'verbose_name_plural': 'Outgoing transmittals'},
        ),
        migrations.AlterModelOptions(
            name='transmittal',
            options={'ordering': ('document_number',), 'verbose_name': 'Transmittal', 'verbose_name_plural': 'Transmittals'},
        ),
        migrations.AlterField(
            model_name='outgoingtransmittal',
            name='document_key',
            field=models.SlugField(unique=True, max_length=250, verbose_name='Document key', blank=True),
        ),
        migrations.AlterField(
            model_name='outgoingtransmittal',
            name='document_number',
            field=models.CharField(max_length=250, verbose_name='Document number', blank=True),
        ),
        migrations.AlterField(
            model_name='transmittal',
            name='document_key',
            field=models.SlugField(unique=True, max_length=250, verbose_name='Document key', blank=True),
        ),
        migrations.AlterField(
            model_name='transmittal',
            name='document_number',
            field=models.CharField(max_length=250, verbose_name='Document number', blank=True),
        ),
    ]
