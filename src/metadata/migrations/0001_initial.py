# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ListEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Order')),
                ('index', models.CharField(max_length=50, verbose_name='Index')),
                ('value', models.CharField(max_length=1024, verbose_name='Value', blank=True)),
            ],
            options={
                'ordering': ('order', 'index'),
                'verbose_name': 'List entry',
                'verbose_name_plural': 'List entries',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ValuesList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('index', models.CharField(max_length=50, verbose_name='Index', db_index=True)),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
            ],
            options={
                'verbose_name': 'Values list',
                'verbose_name_plural': 'Values lists',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='listentry',
            name='values_list',
            field=models.ForeignKey(related_name='values', verbose_name='List', to='metadata.ValuesList'),
            preserve_default=True,
        ),
    ]
