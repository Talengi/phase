# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
from os.path import join
import tempfile
from shutil import rmtree, copytree

from django.test import TestCase

from trsimports.utils import do_import_trs


TEST_CTR = 'test'


class ImportTests(TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix='phasetest_', suffix='_trs')
        self.incoming = join(self.tmpdir, 'incoming')
        self.accepted = join(self.tmpdir, 'accepted')
        self.rejected = join(self.tmpdir, 'rejected')

        os.mkdir(self.accepted)
        os.mkdir(self.rejected)

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
        dest = self.incoming
        copytree(src, dest)

    def test_toto(self):
        self.prepare_fixtures('single_correct_trs')
