# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import logging

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings


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
        path_config = settings.TRS_IMPORTS_PATHS
        ctr_path_config = path_config.get(contractor_id, None)
        if ctr_path_config is None:
            raise ImproperlyConfigured('The "%s" contractor is unknown. '
                                       'Check your configuration.' % contractor_id)

        # Check the existence of the incoming directory
        incoming_dir = ctr_path_config['INCOMING_DIR']
        if not os.path.exists(incoming_dir):
            error = 'The incoming dir does not exist. Check your configuration.'
            raise CommandError(error)

        dir_content = os.listdir(incoming_dir)
        for incoming in dir_content:
            self.import_dir(incoming)

    def import_dir(self, directory):
        """Start the import task for a single directory."""
        pass
