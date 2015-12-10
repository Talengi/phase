# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0002_document_favorited_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='document_number',
            field=models.CharField(max_length=250, null=True, verbose_name='Document number'),
        ),
        migrations.AlterField(
            model_name='document',
            name='document_key',
            field=models.SlugField(unique=True, max_length=250, verbose_name='Document key'),
        ),
    ]
