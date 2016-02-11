# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.db import migrations
from django.conf import settings


def move_exports_dir(*args):
    protected_root = settings.PROTECTED_ROOT
    private_root = settings.PRIVATE_ROOT
    exports_dir = os.path.join(protected_root, 'exports')
    new_dir = os.path.join(private_root, 'exports')

    os.rename(exports_dir, new_dir)


class Migration(migrations.Migration):

    dependencies = [
        ('exports', '0003_export_format'),
    ]

    operations = [
        migrations.RunPython(move_exports_dir)
    ]
