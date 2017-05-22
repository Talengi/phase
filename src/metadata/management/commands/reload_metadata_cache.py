# -*- coding: utf8 -*-



import logging

from django.core.management.base import BaseCommand

from metadata.handlers import populate_values_list_cache


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.info('Populating values list cache')
        populate_values_list_cache()
