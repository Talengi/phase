# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
from os.path import join
import tempfile
from shutil import rmtree, copytree

from django.test import TestCase
from django.core.cache import cache

from transmittals.imports import TrsImport
from transmittals.models import Transmittal, TrsRevision


class TestImports(TestCase):
    fixtures = ['initial_documents']

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

    def test_save_import_to_db(self):
        self.assertEqual(Transmittal.objects.all().count(), 0)
        self.assertEqual(TrsRevision.objects.all().count(), 0)

        trs_import = self.prepare_fixtures('single_correct_trs', 'FAC10005-CTR-CLT-TRS-00001')
        self.assertTrue(trs_import.is_valid())
        trs_import.save()

        self.assertEqual(Transmittal.objects.all().count(), 1)
        self.assertEqual(TrsRevision.objects.all().count(), 1)

    def test_saved_transmittal_data(self):
        trs_import = self.prepare_fixtures('single_correct_trs', 'FAC10005-CTR-CLT-TRS-00001')
        self.assertTrue(trs_import.is_valid())
        trs_import.save()

        transmittal = Transmittal.objects.all()[0]
        self.assertEqual(transmittal.contract_number, 'FAC10005')
        self.assertEqual(transmittal.originator, 'CTR')
        self.assertEqual(transmittal.recipient, 'CLT')
        self.assertEqual(transmittal.sequential_number, 1)

    def test_saved_revision_data(self):
        trs_import = self.prepare_fixtures('single_correct_trs', 'FAC10005-CTR-CLT-TRS-00001')
        self.assertTrue(trs_import.is_valid())
        trs_import.save()

        revision = TrsRevision.objects.all()[0]
        self.assertEqual(revision.document_key, 'FAC10005-CTR-000-EXP-LAY-4891')
        self.assertEqual(revision.originator, 'CTR')
        self.assertEqual(revision.unit, '000')
        self.assertEqual(revision.discipline, 'EXP')
        self.assertEqual(revision.document_type, 'LAY')
        self.assertEqual(revision.sequential_number, '4891')
        self.assertEqual(revision.docclass, 2)
        self.assertEqual(revision.revision, 1)
        self.assertEqual(revision.revision_status, 'IFA')
