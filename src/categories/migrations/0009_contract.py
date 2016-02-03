# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0008_auto_20151127_1124'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.CharField(max_length=50, verbose_name='Number')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('categories', models.ManyToManyField(related_name='contracts', verbose_name='Categories', to='categories.Category')),
            ],
        ),
    ]
