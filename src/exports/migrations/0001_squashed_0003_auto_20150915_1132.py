# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Export',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('querystring', models.TextField(help_text='The search filter querystring', verbose_name='Querystring')),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created on')),
                ('category', models.ForeignKey(verbose_name='Category', to='categories.Category')),
                ('owner', models.ForeignKey(verbose_name='Owner', to=settings.AUTH_USER_MODEL)),
                ('status', models.CharField(default='new', max_length=30, verbose_name='Status', choices=[('new', 'New'), ('processing', 'Processing'), ('done', 'Done')])),
            ],
            options={
                'verbose_name': 'Export',
                'verbose_name_plural': 'Exports',
            },
        ),
    ]
