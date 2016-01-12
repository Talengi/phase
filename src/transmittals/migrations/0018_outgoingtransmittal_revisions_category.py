# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0008_auto_20151127_1124'),
        ('transmittals', '0017_remove_outgoingtransmittal_related_documents'),
    ]

    operations = [
        migrations.AddField(
            model_name='outgoingtransmittal',
            name='revisions_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name='From category', blank=True, to='categories.Category', null=True),
        ),
    ]
