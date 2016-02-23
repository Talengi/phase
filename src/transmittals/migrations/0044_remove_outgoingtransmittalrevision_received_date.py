# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0043_outgoingtransmittalrevision_error_notified'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='outgoingtransmittalrevision',
            name='received_date',
        ),
    ]
