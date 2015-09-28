# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings

from exports.models import Export


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.info('Cleaning old exports')

        now = timezone.now()
        clean_before = now - timedelta(days=settings.EXPORTS_VALIDITY_DURATION)
        exports_to_clean = Export.objects.filter(created_on__lte=clean_before)

        export_dir = os.path.realpath(settings.PRIVATE_ROOT)
        for export in exports_to_clean:

            # Remove the actual export file
            filepath = os.path.realpath(export.get_filepath())
            logger.info('Attempting to remove {}'.format(filepath))
            if os.path.exists(filepath) and filepath.startswith(export_dir):
                os.remove(filepath)
            else:
                logger.warning('Cannot delete {}'.format(filepath))

        # Remove db objects
        exports_to_clean.delete()
