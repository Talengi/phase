# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
from os.path import join
import tempfile
from shutil import rmtree, copytree

from django.test import TestCase
from django.core.cache import cache

from transmittals.imports import TrsImport


TEST_CTR = 'test'


def touch(path):
    """Simply creates an empty file."""
    open(path, 'a').close()


class TransmittalsValidationTests(TestCase):
    def setUp(self):
        # Clear the values list cache
        cache.clear()

        self.tmpdir = tempfile.mkdtemp(prefix='phasetest_', suffix='_trs')
        self.incoming = join(self.tmpdir, 'incoming')
        self.tobechecked = join(self.tmpdir, 'tobechecked')
        self.accepted = join(self.tmpdir, 'accepted')
        self.rejected = join(self.tmpdir, 'rejected')

        os.mkdir(self.accepted)
        os.mkdir(self.rejected)
        os.mkdir(self.tobechecked)

        self.config = {
            'INCOMING_DIR': self.incoming,
            'REJECTED_DIR': self.rejected,
            'TO_BE_CHECKED_DIR': self.tobechecked,
            'ACCEPTED_DIR': self.accepted,
            'EMAIL_LIST': ['test@phase.fr'],
        }

    def tearDown(self):
        if os.path.exists(self.tmpdir):
            rmtree(self.tmpdir)

    def prepare_fixtures(self, fixtures_dir, trs_dir):
        """Create the fixtures import dir."""
        src = os.path.join(
            os.path.dirname(__file__),
            'fixtures',
            fixtures_dir
        )
        dest = self.config['INCOMING_DIR']
        copytree(src, dest)

        trs_fullname = join(self.config['INCOMING_DIR'], trs_dir)
        trs_import = TrsImport(
            trs_fullname,
            tobechecked_dir=self.config['TO_BE_CHECKED_DIR'],
            accepted_dir=self.config['ACCEPTED_DIR'],
            rejected_dir=self.config['REJECTED_DIR'],
            email_list=self.config['EMAIL_LIST'],
        )
        return trs_import


class DirectoryContentTests(TransmittalsValidationTests):
    fixtures = ['initial_documents']

    def test_invalid_directory_name(self):
        trs_import = self.prepare_fixtures('invalid_trs_dirname', 'I-Love-Bananas')
        self.assertTrue('invalid_dirname' in trs_import.errors['global_errors'])

    def test_missing_csv(self):
        trs_import = self.prepare_fixtures('missing_csv', 'FAC10005-CTR-CLT-TRS-00001')
        self.assertTrue('missing_csv' in trs_import.errors['global_errors'])

    def test_wrong_csv_filename(self):
        trs_import = self.prepare_fixtures('wrong_csv_filename', 'FAC10005-CTR-CLT-TRS-00001')
        self.assertTrue('missing_csv' in trs_import.errors['global_errors'])

    def test_csv_columns(self):
        trs_import = self.prepare_fixtures('wrong_csv_columns', 'FAC10005-CTR-CLT-TRS-00001')
        self.assertTrue('csv_columns' in trs_import.errors['global_errors'])

    def test_not_enough_pdfs(self):
        trs_import = self.prepare_fixtures('not_enough_pdfs', 'FAC10005-CTR-CLT-TRS-00001')
        self.assertTrue('wrong_pdf_count' in trs_import.errors['global_errors'])

    def test_too_many_pdfs(self):
        trs_import = self.prepare_fixtures('too_many_pdfs', 'FAC10005-CTR-CLT-TRS-00001')
        self.assertTrue('wrong_pdf_count' in trs_import.errors['global_errors'])

    def test_too_many_native_files(self):
        trs_import = self.prepare_fixtures('too_many_native_files', 'FAC10005-CTR-CLT-TRS-00001')
        self.assertTrue('native_files' in trs_import.errors['global_errors'])

    def test_valid_transmittal(self):
        trs_import = self.prepare_fixtures('single_correct_trs', 'FAC10005-CTR-CLT-TRS-00001')
        self.assertEqual(trs_import.errors, {})


class CSVContentTests(TransmittalsValidationTests):
    fixtures = ['initial_documents']

    def test_missing_csv_data(self):
        trs_import = self.prepare_fixtures('missing_data', 'FAC10005-CTR-CLT-TRS-00001')
        self.assertTrue('missing_data' in trs_import.errors['csv_content'][2])

    def test_missing_document(self):
        trs_import = self.prepare_fixtures('missing_document', 'FAC10005-CTR-CLT-TRS-00001')
        self.assertTrue('document_not_found' in trs_import.errors['csv_content'][2])

    def test_missing_pdf_file(self):
        trs_import = self.prepare_fixtures('missing_pdf', 'FAC10005-CTR-CLT-TRS-00001')
        self.assertTrue('missing_pdf' in trs_import.errors['csv_content'][2])

    def test_form_validation_error(self):
        trs_import = self.prepare_fixtures('form_error', 'FAC10005-CTR-CLT-TRS-00001')
        self.assertTrue('data_validation' in trs_import.errors['csv_content'][2])

    def test_different_title(self):
        trs_import = self.prepare_fixtures('different_title', 'FAC10005-CTR-CLT-TRS-00001')
        self.assertTrue('wrong_title' in trs_import.errors['csv_content'][2])

    def test_incorrect_revision_number(self):
        trs_import = self.prepare_fixtures('incorrect_revision', 'FAC10005-CTR-CLT-TRS-00001')
        self.assertTrue(5 in trs_import.errors['revisions']['FAC10005-CTR-000-EXP-LAY-4891'])

    def test_incorrect_revision_format(self):
        trs_import = self.prepare_fixtures('revision_format', 'FAC10005-CTR-CLT-TRS-00001')
        self.assertTrue('revision_format' in trs_import.errors['csv_content'][2])

    def test_non_following_revision_numbers(self):
        trs_import = self.prepare_fixtures('non_following_revisions', 'FAC10005-CTR-CLT-TRS-00001')
        self.assertFalse(1 in trs_import.errors['revisions']['FAC10005-CTR-000-EXP-LAY-4891'])
        self.assertFalse(2 in trs_import.errors['revisions']['FAC10005-CTR-000-EXP-LAY-4891'])
        self.assertFalse(3 in trs_import.errors['revisions']['FAC10005-CTR-000-EXP-LAY-4891'])
        self.assertFalse(4 in trs_import.errors['revisions']['FAC10005-CTR-000-EXP-LAY-4891'])
        self.assertTrue(6 in trs_import.errors['revisions']['FAC10005-CTR-000-EXP-LAY-4891'])


class DirRenameTests(TransmittalsValidationTests):

    def test_trs_is_moved_to_rejected(self):
        """The trs must be moved to rejected directory"""
        trs_import = self.prepare_fixtures('missing_csv', 'FAC10005-CTR-CLT-TRS-00001')

        dirpath = join(self.rejected, 'FAC10005-CTR-CLT-TRS-00001')

        trs_import.move_to_rejected()
        self.assertTrue(os.path.exists(dirpath))
        self.assertFalse(os.path.exists(trs_import.trs_dir))

    def test_old_dir_exists_in_rejected(self):
        """When the dir already exists in rejected, it must be overwritten."""
        trs_import = self.prepare_fixtures('missing_csv', 'FAC10005-CTR-CLT-TRS-00001')

        dirpath = join(self.rejected, 'FAC10005-CTR-CLT-TRS-00001')
        os.mkdir(dirpath)

        filepath = join(dirpath, 'old_file')
        touch(filepath)
        self.assertTrue(os.path.exists(filepath))

        trs_import.move_to_rejected()
        self.assertTrue(os.path.exists(dirpath))
        self.assertFalse(os.path.exists(filepath))
