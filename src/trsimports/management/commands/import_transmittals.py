# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import logging

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from trsimports.models import TrsImport


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

        # Check directories permissions
        self.assert_permissions(ctr_config['INCOMING_DIR'])
        self.assert_permissions(ctr_config['REJECTED_DIR'])
        self.assert_permissions(ctr_config['TO_BE_CHECKED_DIR'])
        self.assert_permissions(ctr_config['ACCEPTED_DIR'])

        # Start import
        incoming_dir = ctr_config['INCOMING_DIR']
        dir_content = os.listdir(incoming_dir)
        for incoming in dir_content:
            fullname = os.path.join(incoming_dir, incoming)
            self.import_dir(fullname, ctr_config)

    def assert_permissions(self, path):
        """Raise an error if the given path is not writeable."""
        if not os.path.exists(path):
            error = 'The directory "%s" does not exist.' % path
            raise CommandError(error)

        permissions = os.R_OK | os.W_OK | os.X_OK
        if not os.access(path, permissions):
            error = 'The directory "%s" is not writeable.' % path
            raise CommandError(error)

    def import_dir(self, directory, config):
        """Start the import task for a single directory."""
        logger.info('Starting import of trs in %s' % directory)

        trsImport = TrsImport(
            directory,
            tobechecked_dir=config['TO_BE_CHECKED_DIR'],
            accepted_dir=config['ACCEPTED_DIR'],
            rejected_dir=config['REJECTED_DIR'],
            email_list=config['EMAIL_LIST'],
        )
        trsImport.do_import()
