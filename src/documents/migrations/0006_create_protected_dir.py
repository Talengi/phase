# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from os import path

from django.db import migrations
from django.conf import settings


def create_protected_dir(*args):
    # Create "protected" dir
    protected_root = settings.PROTECTED_ROOT
    if not path.exists(protected_root):
        os.makedirs(protected_root)

    # Move private dirs to new protected dir
    private_root = settings.PRIVATE_ROOT
    if path.exists(private_root):
        private_dirs = os.listdir(private_root)
        for dirname in private_dirs:
            if dirname == 'revisions':
                continue

            full_name = private_root.child(dirname)
            new_name = protected_root.child(dirname)
            os.rename(full_name, new_name)


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0005_auto_20151210_1045'),
    ]

    operations = [
        migrations.RunPython(create_protected_dir)
    ]
