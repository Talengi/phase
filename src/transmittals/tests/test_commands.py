# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import stat
from io import StringIO
from shutil import rmtree, copytree

from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError
from django.core.exceptions import ImproperlyConfigured
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from mock import patch

from transmittals.models import Transmittal
from categories.factories import CategoryFactory


IMPORT_COMMAND = 'import_transmittals'
TEST_CTR = 'test'


class ImportCommandTests(TestCase):

    def setUp(self):
        doc_category = CategoryFactory()
        self.doc_category_path = '{}/{}'.format(
            doc_category.organisation.slug,
            doc_category.category_template.slug)

        trs_content_type = ContentType.objects.get_for_model(Transmittal)
        trs_category = CategoryFactory(category_template__metadata_model=trs_content_type)
        self.trs_category_path = '{}/{}'.format(
            trs_category.organisation.slug,
            trs_category.category_template.slug)

        path_config = settings.TRS_IMPORTS_CONFIG
        ctr_path_config = path_config.get(TEST_CTR)
        self.import_root = settings.TRS_IMPORTS_ROOT
        self.incoming_dir = ctr_path_config['INCOMING_DIR']
        self.rejected_dir = ctr_path_config['REJECTED_DIR']
        self.to_be_checked_dir = ctr_path_config['TO_BE_CHECKED_DIR']
        self.accepted_dir = ctr_path_config['ACCEPTED_DIR']

    def tearDown(self):
        if all((
            self.import_root.exists(),
            self.import_root.startswith('/tmp/'),
        )):
            rmtree(self.import_root)

    def prepare_import_dir(self, directory=None):
        """Create the root import dir."""
        os.mkdir(self.import_root)

        if directory is not None:
            src = os.path.join(
                os.path.dirname(__file__),
                'fixtures',
                directory
            )
            dest = self.incoming_dir
            copytree(src, dest)
        else:
            os.mkdir(self.incoming_dir)

    def test_missing_paramateres(self):
        """The command must be called with the ctr as an argument."""
        f = StringIO()

        with self.assertRaises(CommandError) as cm:
            call_command(IMPORT_COMMAND, stderr=f)

        error = 'Usage: python manage.py import_transmittals <contractor_id> <doc_category> <trs_category>'
        self.assertEqual(str(cm.exception), error)

    def test_incorrect_ctr_parameter(self):
        """An exception must be raised when the contractor id is unknown."""
        f = StringIO()

        with self.assertRaises(ImproperlyConfigured) as cm:
            call_command(
                IMPORT_COMMAND,
                'wrong_ctr',
                self.doc_category_path,
                self.trs_category_path,
                stderr=f)

        error = 'The "wrong_ctr" contractor is unknown. Check your configuration.'
        self.assertEqual(str(cm.exception), error)

    def test_incorrect_category_parameters(self):
        """An exception must be raised when the category does not exist."""
        f = StringIO()

        with self.assertRaises(CommandError) as cm:
            call_command(IMPORT_COMMAND, TEST_CTR, 'wrong_cat', 'wrong_cat', stderr=f)

        error = 'The document category is unknown. Check your configuration.'
        self.assertEqual(str(cm.exception), error)

    def test_wrong_transmittal_category(self):
        """An exception must be raised when the transmittal category does not host Transmittals documents."""
        f = StringIO()

        with self.assertRaises(CommandError) as cm:
            call_command(
                IMPORT_COMMAND,
                TEST_CTR,
                self.doc_category_path,
                self.doc_category_path,
                stderr=f)

        error = 'The transmittal category should host Transmittal documents.'
        self.assertEqual(str(cm.exception), error)

    def test_incoming_dir_does_not_exist(self):
        """An exception must be raised when the incoming dir does not exist."""
        f = StringIO()

        with self.assertRaises(CommandError) as cm:
            call_command(
                IMPORT_COMMAND,
                TEST_CTR,
                self.doc_category_path,
                self.trs_category_path,
                stderr=f)

        error = 'The directory "/tmp/test_ctr_clt/incoming" does not exist.'
        self.assertEqual(str(cm.exception), error)

    def test_rejected_dir_does_not_exist(self):
        """An exception must be raised when the error dir does not exist."""
        f = StringIO()
        self.prepare_import_dir('empty_dirs')

        with self.assertRaises(CommandError) as cm:
            call_command(
                IMPORT_COMMAND,
                TEST_CTR,
                self.doc_category_path,
                self.trs_category_path,
                stderr=f)

        error = 'The directory "/tmp/test_ctr_clt/rejected" does not exist.'
        self.assertEqual(str(cm.exception), error)

    def test_rejected_dir_is_not_writeable(self):
        """An exception must be raised when the error dir cannot be written."""
        f = StringIO()
        self.prepare_import_dir('empty_dirs')

        os.mkdir(self.rejected_dir)
        wrong_perms = stat.S_IRUSR | stat.S_IXUSR  # No write perm
        os.chmod(self.rejected_dir, wrong_perms)

        with self.assertRaises(CommandError) as cm:
            call_command(
                IMPORT_COMMAND,
                TEST_CTR,
                self.doc_category_path,
                self.trs_category_path,
                stderr=f)

        error = 'The directory "/tmp/test_ctr_clt/rejected" is not writeable.'
        self.assertEqual(str(cm.exception), error)

    @patch('transmittals.management.commands.import_transmittals.Command.import_dir')
    def test_calling_import_method(self, import_dir):
        """When a directory is found, the import method must be fired"""
        f = StringIO()
        self.prepare_import_dir('empty_dirs')
        os.mkdir(self.rejected_dir)
        os.mkdir(self.accepted_dir)
        os.mkdir(self.to_be_checked_dir)

        call_command(
            IMPORT_COMMAND,
            TEST_CTR,
            self.doc_category_path,
            self.trs_category_path,
            stderr=f)
        self.assertEqual(import_dir.call_count, 3)

    def test_incorrect_trs_validator_option(self):
        f = StringIO()

        with self.assertRaises(CommandError) as cm:
            call_command(
                IMPORT_COMMAND,
                TEST_CTR,
                self.doc_category_path,
                self.trs_category_path,
                trs_validator='toto',
                stderr=f)

        error = 'The validator toto does not exist.'
        self.assertEqual(str(cm.exception), error)

    def test_invalid_trs_validator_option(self):
        f = StringIO()

        with self.assertRaises(CommandError) as cm:
            call_command(
                IMPORT_COMMAND,
                TEST_CTR,
                self.doc_category_path,
                self.trs_category_path,
                trs_validator='documents.models.Document',
                stderr=f)

        error = 'The validator documents.models.Document is invalid. Must be a Validator subclass.'
        self.assertEqual(str(cm.exception), error)

    def test_incorrect_csv_validator_option(self):
        f = StringIO()

        with self.assertRaises(CommandError) as cm:
            call_command(
                IMPORT_COMMAND,
                TEST_CTR,
                self.doc_category_path,
                self.trs_category_path,
                csv_line_validator='toto',
                stderr=f)

        error = 'The validator toto does not exist.'
        self.assertEqual(str(cm.exception), error)

    def test_invalid_csv_validator_option(self):
        f = StringIO()

        with self.assertRaises(CommandError) as cm:
            call_command(
                IMPORT_COMMAND,
                TEST_CTR,
                self.doc_category_path,
                self.trs_category_path,
                csv_line_validator='documents.models.Metadata',
                stderr=f)

        error = 'The validator documents.models.Metadata is invalid. Must be a Validator subclass.'
        self.assertEqual(str(cm.exception), error)
