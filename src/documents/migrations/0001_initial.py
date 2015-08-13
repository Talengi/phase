# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('document_key', models.SlugField(unique=True, max_length=250, verbose_name='Document number')),
                ('title', models.TextField(verbose_name='Title')),
                ('created_on', models.DateField(default=django.utils.timezone.now, verbose_name='Created on')),
                ('updated_on', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Updated on')),
                ('is_indexable', models.BooleanField(default=True, verbose_name='Indexable')),
                ('current_revision', models.PositiveIntegerField(verbose_name='Revision')),
                ('current_revision_date', models.DateField(null=True, verbose_name='Revision Date', blank=True)),
                ('category', models.ForeignKey(related_name='documents', verbose_name='Category', to='categories.Category')),
            ],
            options={
                'verbose_name': 'Document',
                'verbose_name_plural': 'Documents',
                'permissions': (('can_control_document', 'Can control document'),),
            },
        ),
    ]
