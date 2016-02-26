# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_auto_20160225_1510'),
        ('transmittals', '0048_auto_20160224_1526'),
    ]

    operations = [
        migrations.AddField(
            model_name='trsrevision',
            name='originator_new',
            field=models.ForeignKey(verbose_name='Originator', to='accounts.Entity', null=True),
        ),
    ]
