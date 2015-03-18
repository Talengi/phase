# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase

from transmittals.factories import TransmittalFactory


class TransmittalModelTests(TestCase):

    def setUp(self):
        pass

    def test_refuse_trs_with_wrong_state(self):
        trs = TransmittalFactory(status='accepted')
        with self.assertRaises(RuntimeError):
            trs.refuse()

        trs = TransmittalFactory(status='refused')
        with self.assertRaises(RuntimeError):
            trs.refuse()
