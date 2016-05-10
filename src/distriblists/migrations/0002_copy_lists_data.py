# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, connection


def copy_data(apps, schema_editor):
    cursor = connection.cursor()
    cursor.execute('INSERT INTO {} SELECT * FROM {}'.format(
        'distriblists_distributionlist',
        'reviews_distributionlist'
    ))


class Migration(migrations.Migration):

    dependencies = [
        ('distriblists', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(copy_data, migrations.RunPython.noop),
    ]
