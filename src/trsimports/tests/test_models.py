# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
from os.path import join
import tempfile
from shutil import rmtree, copytree

from django.test import TestCase

from trsimports.models import TrsImport


TEST_CTR = 'test'


class TransmittalsValidationTests(TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix='phasetest_', suffix='_trs')
        incoming = join(self.tmpdir, 'incoming')
        tobechecked = join(self.tmpdir, 'tobechecked')
        accepted = join(self.tmpdir, 'accepted')
        rejected = join(self.tmpdir, 'rejected')

        os.mkdir(accepted)
        os.mkdir(rejected)
        os.mkdir(tobechecked)

        self.config = {
            'INCOMING_DIR': incoming,
            'REJECTED_DIR': rejected,
            'TO_BE_CHECKED_DIR': tobechecked,
            'ACCEPTED_DIR': accepted,
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
        trsImport = TrsImport(
            trs_fullname,
            tobechecked_dir=self.config['TO_BE_CHECKED_DIR'],
            accepted_dir=self.config['ACCEPTED_DIR'],
            rejected_dir=self.config['REJECTED_DIR'],
        )
        return trsImport

    def test_invalid_directory_name(self):
        trsImport = self.prepare_fixtures('invalid_trs_dirname', 'I-Love-Bananas')
        self.assertTrue('invalid_dirname' in trsImport.errors)

    def test_missing_csv(self):
        trsImport = self.prepare_fixtures('missing_csv', 'FAC10005-CTR-CLT-TRS-00001')
        self.assertTrue('missing_csv' in trsImport.errors)

    def test_not_enough_pdfs(self):
        trsImport = self.prepare_fixtures('not_enough_pdfs', 'FAC10005-CTR-CLT-TRS-00001')
        self.assertTrue('wrong_pdf_count' in trsImport.errors)

    def test_too_many_pdfs(self):
        trsImport = self.prepare_fixtures('too_many_pdfs', 'FAC10005-CTR-CLT-TRS-00001')
        self.assertTrue('wrong_pdf_count' in trsImport.errors)
