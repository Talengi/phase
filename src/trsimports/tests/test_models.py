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

    def prepare_fixtures(self, fixtures_dir):
        """Create the fixtures import dir."""
        src = os.path.join(
            os.path.dirname(__file__),
            'fixtures',
            fixtures_dir
        )
        dest = self.config['INCOMING_DIR']
        copytree(src, dest)

    def test_invalid_directory_name(self):
        self.prepare_fixtures('invalid_trs_dirname')
        importdir = join(self.config['INCOMING_DIR'], 'I-Love-Bananas')

        trsImport = TrsImport(
            importdir,
            tobechecked_dir=self.config['TO_BE_CHECKED_DIR'],
            accepted_dir=self.config['ACCEPTED_DIR'],
            rejected_dir=self.config['REJECTED_DIR'],
        )
        self.assertTrue('invalid_dirname' in trsImport.errors)
