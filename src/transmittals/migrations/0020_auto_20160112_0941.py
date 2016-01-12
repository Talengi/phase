# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0019_fill_revisions_categories'),
    ]

    operations = [
        migrations.AlterField(
            model_name='outgoingtransmittal',
            name='revisions_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name='From category', to='categories.Category'),
        ),
    ]
