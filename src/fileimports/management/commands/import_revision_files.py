# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import logging

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from fileimports.tasks import import_file


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Look for revision files to be imported'

    def handle(self, *args, **options):
        import_dir = settings.IMPORT_ROOT

        if not os.path.isdir(import_dir):
            error = 'The directory "%s" does not exist' % import_dir
            raise CommandError(error)

        files = os.listdir(import_dir)
        for file_ in files:
            import_file.delay(os.path.join(import_dir, file_))
