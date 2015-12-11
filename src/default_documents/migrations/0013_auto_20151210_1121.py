# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0012_auto_20151202_1413'),
    ]

    operations = [
        migrations.AddField(
            model_name='contractordeliverable',
            name='document_number',
            field=models.CharField(max_length=250, null=True, verbose_name='Document number'),
        ),
        migrations.AddField(
            model_name='correspondence',
            name='document_number',
            field=models.CharField(max_length=250, null=True, verbose_name='Document number'),
        ),
        migrations.AddField(
            model_name='demometadata',
            name='document_number',
            field=models.CharField(max_length=250, null=True, verbose_name='Document number'),
        ),
        migrations.AddField(
            model_name='minutesofmeeting',
            name='document_number',
            field=models.CharField(max_length=250, null=True, verbose_name='Document number'),
        ),
        migrations.AlterField(
            model_name='contractordeliverable',
            name='document_key',
            field=models.SlugField(unique=True, max_length=250, verbose_name='Document key'),
        ),
        migrations.AlterField(
            model_name='correspondence',
            name='document_key',
            field=models.SlugField(unique=True, max_length=250, verbose_name='Document key'),
        ),
        migrations.AlterField(
            model_name='demometadata',
            name='document_key',
            field=models.SlugField(unique=True, max_length=250, verbose_name='Document key'),
        ),
        migrations.AlterField(
            model_name='minutesofmeeting',
            name='document_key',
            field=models.SlugField(unique=True, max_length=250, verbose_name='Document key'),
        ),
    ]
