# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import logging

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from trsimports.utils import do_import_trs


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Run the transmittals sheet import command.

    This is the entry point to the transmittals import feature.

    """
    args = '<contractor_id>'
    help = 'Import existing transmittals for a given contractor.'

    def handle(self, *args, **options):
        if len(args) != 1:
            error = 'You must provide a contractor id as an argument'
            raise CommandError(error)

        # Get configuration for the given contractor
        contractor_id = args[0]
        config = settings.TRS_IMPORTS_CONFIG
        ctr_config = config.get(contractor_id, None)
        if ctr_config is None:
            raise ImproperlyConfigured('The "%s" contractor is unknown. '
                                       'Check your configuration.' % contractor_id)

        # Check the existence of the incoming directory
        incoming_dir = ctr_config['INCOMING_DIR']
        if not os.path.exists(incoming_dir):
            error = 'The incoming dir does not exist. Check your configuration.'
            raise CommandError(error)

        dir_content = os.listdir(incoming_dir)
        for incoming in dir_content:
            fullname = os.path.join(incoming_dir, incoming)
            self.import_dir(fullname, ctr_config)

    def import_dir(self, directory, config):
        """Start the import task for a single directory."""
        logger.info('Starting import of trs in %s' % directory)
        do_import_trs(directory, config)
