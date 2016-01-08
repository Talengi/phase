# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('default_documents', '0016_auto_20160108_1010'),
    ]

    operations = [
        migrations.AddField(
            model_name='contractordeliverablerevision',
            name='under_preparation_by',
            field=models.ForeignKey(related_name='+', verbose_name='Under preparation by', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
