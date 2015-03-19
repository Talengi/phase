# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
from os.path import join
import tempfile
from shutil import rmtree, copytree

from django.test import TestCase

from transmittals.factories import TransmittalFactory


def touch(path):
    """Simply creates an empty file."""
    open(path, 'a').close()


class TransmittalModelTests(TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix='phasetest_', suffix='_trs')
        self.incoming = join(self.tmpdir, 'incoming')
        self.tobechecked = join(self.tmpdir, 'tobechecked')
        self.accepted = join(self.tmpdir, 'accepted')
        self.rejected = join(self.tmpdir, 'rejected')

        os.mkdir(self.accepted)
        os.mkdir(self.rejected)
        os.mkdir(self.tobechecked)

        self.transmittal = TransmittalFactory(
            transmittal_key='FAC10005-CTR-CLT-TRS-00001',
            status='tobechecked',
            tobechecked_dir=self.tobechecked,
            accepted_dir=self.accepted,
            rejected_dir=self.rejected,
            contractor='test')
        os.mkdir(self.transmittal.full_tobechecked_name)

    def tearDown(self):
        if os.path.exists(self.tmpdir):
            rmtree(self.tmpdir)

    def test_reject_trs_with_wrong_state(self):
        trs = TransmittalFactory(status='accepted')
        with self.assertRaises(RuntimeError):
            trs.reject()

        trs = TransmittalFactory(status='refused')
        with self.assertRaises(RuntimeError):
            trs.reject()

    def test_reject_moves_trs_to_rejected_directory(self):
        self.assertTrue(os.path.exists(self.transmittal.full_tobechecked_name))
        self.assertFalse(os.path.exists(self.transmittal.full_rejected_name))

        self.transmittal.reject()
        self.assertFalse(os.path.exists(self.transmittal.full_tobechecked_name))
        self.assertTrue(os.path.exists(self.transmittal.full_rejected_name))

    def test_reject_with_already_existing_rejected_directory(self):
        touch(join(self.transmittal.full_tobechecked_name, 'toto.csv'))

        copytree(
            self.transmittal.full_tobechecked_name,
            self.transmittal.full_rejected_name)
        self.assertTrue(os.path.exists(self.transmittal.full_tobechecked_name))
        self.assertTrue(os.path.exists(self.transmittal.full_rejected_name))

        self.transmittal.reject()
        self.assertEqual(self.transmittal.status, 'rejected')
        self.assertFalse(os.path.exists(self.transmittal.full_tobechecked_name))
        self.assertTrue(os.path.exists(self.transmittal.full_rejected_name))
