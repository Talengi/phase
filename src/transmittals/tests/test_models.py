# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase

from transmittals.factories import TransmittalFactory


class TransmittalModelTests(TestCase):

    def setUp(self):
        pass

    def test_reject_trs_with_wrong_state(self):
        trs = TransmittalFactory(status='accepted')
        with self.assertRaises(RuntimeError):
            trs.reject()

        trs = TransmittalFactory(status='refused')
        with self.assertRaises(RuntimeError):
            trs.reject()

    def test_directory_properties(self):
        trs = TransmittalFactory(
            transmittal_key='FAC10005-CTR-CLT-TRS-00001',
            status='tobechecked')

        self.assertEqual(
            trs.full_tobechecked_name,
            '/tmp/test_ctr_clt/tobechecked/FAC10005-CTR-CLT-TRS-00001')
        self.assertEqual(
            trs.full_accepted_name,
            '/tmp/test_ctr_clt/accepted/FAC10005-CTR-CLT-TRS-00001')
        self.assertEqual(
            trs.full_rejected_name,
            '/tmp/test_ctr_clt/rejected/FAC10005-CTR-CLT-TRS-00001')

    def test_reject_moves_trs_to_rejected_directory(self):
        trs = TransmittalFactory(status='accepted')
