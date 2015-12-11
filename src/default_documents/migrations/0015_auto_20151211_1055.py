# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0014_fill_document_numbers'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contractordeliverable',
            options={'ordering': ('document_number',)},
        ),
        migrations.AlterModelOptions(
            name='demometadata',
            options={'ordering': ('document_number',)},
        ),
        migrations.AlterModelOptions(
            name='minutesofmeeting',
            options={'ordering': ('document_number',)},
        ),
        migrations.AlterField(
            model_name='contractordeliverable',
            name='document_key',
            field=models.SlugField(unique=True, max_length=250, verbose_name='Document key', blank=True),
        ),
        migrations.AlterField(
            model_name='contractordeliverable',
            name='document_number',
            field=models.CharField(max_length=250, verbose_name='Document number', blank=True),
        ),
        migrations.AlterField(
            model_name='correspondence',
            name='document_key',
            field=models.SlugField(unique=True, max_length=250, verbose_name='Document key', blank=True),
        ),
        migrations.AlterField(
            model_name='correspondence',
            name='document_number',
            field=models.CharField(max_length=250, verbose_name='Document number', blank=True),
        ),
        migrations.AlterField(
            model_name='demometadata',
            name='document_key',
            field=models.SlugField(unique=True, max_length=250, verbose_name='Document key', blank=True),
        ),
        migrations.AlterField(
            model_name='demometadata',
            name='document_number',
            field=models.CharField(max_length=250, verbose_name='Document number', blank=True),
        ),
        migrations.AlterField(
            model_name='minutesofmeeting',
            name='document_key',
            field=models.SlugField(unique=True, max_length=250, verbose_name='Document key', blank=True),
        ),
        migrations.AlterField(
            model_name='minutesofmeeting',
            name='document_number',
            field=models.CharField(max_length=250, verbose_name='Document number', blank=True),
        ),
    ]
