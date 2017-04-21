# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import logging
from optparse import make_option
import importlib

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from annoying.functions import get_object_or_None

from categories.models import Category
from transmittals.imports import TrsImport
from transmittals.validation import Validator


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Run the transmittals sheet import command.

    This is the entry point to the transmittals import feature.

    """
    args = '<contractor_id> <doc_category> <trs_category>'
    help = 'Import existing transmittals for a given contractor.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--trs-validator',
            action='store',
            dest='trs_validator',
            default=False,
            help='Choose a custom global validator class')
        parser.add_argument(
            '--csv-line-validator',
            action='store',
            dest='csv_line_validator',
            default=False,
            help='Choose a custom single csv line validator class')

    def handle(self, *args, **options):
        from transmittals.models import Transmittal

        if len(args) != 3:
            error = 'Usage: python manage.py import_transmittals {}'.format(self.args)
            raise CommandError(error)

        # Import validators
        TrsValidator = None
        trs_validator = options['trs_validator']
        if trs_validator:
            TrsValidator = self.import_validator(trs_validator)

        CsvLineValidator = None
        csv_line_validator = options['csv_line_validator']
        if csv_line_validator:
            CsvLineValidator = self.import_validator(csv_line_validator)

        # Get configuration for the given contractor
        contractor_id = args[0]
        config = settings.TRS_IMPORTS_CONFIG
        ctr_config = config.get(contractor_id, None)
        if ctr_config is None:
            raise ImproperlyConfigured('The "%s" contractor is unknown. '
                                       'Check your configuration.' % contractor_id)

        # Get categories
        doc_category = self.get_category(args[1])
        if doc_category is None:
            error = 'The document category is unknown. Check your configuration.'
            raise CommandError(error)

        trs_category = self.get_category(args[2])
        if trs_category is None:
            error = 'The transmittal category is unknown. Check your configuration.'
            raise CommandError(error)

        model_class = trs_category.category_template.metadata_model.model_class()
        if model_class != Transmittal:
            error = 'The transmittal category should host Transmittal documents.'
            raise CommandError(error)

        # Check directories permissions
        self.assert_permissions(ctr_config['INCOMING_DIR'])
        self.assert_permissions(ctr_config['REJECTED_DIR'])
        self.assert_permissions(ctr_config['TO_BE_CHECKED_DIR'])
        self.assert_permissions(ctr_config['ACCEPTED_DIR'])

        # Start import
        incoming_dir = ctr_config['INCOMING_DIR']
        dir_content = sorted(os.listdir(incoming_dir))
        for incoming in dir_content:
            fullname = os.path.join(incoming_dir, incoming)
            self.import_dir(
                fullname,
                ctr_config,
                contractor_id,
                doc_category, trs_category,
                TrsValidator, CsvLineValidator)

    def get_category(self, path):
        """Takes a string "organisation_slug/category_slug" and returns a category."""
        slugs = path.split('/')

        if len(slugs) != 2:
            return None

        qs = Category.objects \
            .filter(organisation__slug=slugs[0]) \
            .filter(category_template__slug=slugs[1])
        return get_object_or_None(qs)

    def assert_permissions(self, path):
        """Raise an error if the given path is not writeable."""
        if not os.path.exists(path):
            error = 'The directory "%s" does not exist.' % path
            raise CommandError(error)

        permissions = os.R_OK | os.W_OK | os.X_OK
        if not os.access(path, permissions):
            error = 'The directory "%s" is not writeable.' % path
            raise CommandError(error)

    def import_dir(self, directory, config, contractor, doc_category,
                   trs_category, TrsValidator, CsvLineValidator):
        """Start the import task for a single directory."""
        logger.info('Starting import of trs in %s' % directory)

        trsImport = TrsImport(
            directory,
            tobechecked_dir=config['TO_BE_CHECKED_DIR'],
            accepted_dir=config['ACCEPTED_DIR'],
            rejected_dir=config['REJECTED_DIR'],
            email_list=config['EMAIL_LIST'],
            contractor=contractor,
            doc_category=doc_category,
            trs_category=trs_category,
            trs_validator=TrsValidator,
            csv_line_validator=CsvLineValidator,
        )
        trsImport.do_import()

    def import_validator(self, validator_path):
        """Import a validator class from it's path."""
        try:
            path = validator_path.split('.')
            module_path = '.'.join(path[0:-1])
            module = importlib.import_module(module_path)
            class_name = path[-1]
            TrsValidator = getattr(module, class_name)
        except:
            error = 'The validator {} does not exist.'.format(validator_path)
            raise CommandError(error)

        if not issubclass(TrsValidator, Validator):
            error = 'The validator {} is invalid. Must be a Validator subclass.'.format(
                validator_path)
            raise CommandError(error)

        return TrsValidator
