# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from io import StringIO

from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError
from django.core.exceptions import ImproperlyConfigured


IMPORT_COMMAND = 'import_transmittals'
TEST_CTR = 'test'


class ImportCommandTests(TestCase):

    def test_missing_ctr_parameter(self):
        """The command must be called with the ctr as an argument."""
        f = StringIO()

        with self.assertRaises(CommandError) as cm:
            call_command(IMPORT_COMMAND, stderr=f)

            error = 'You must provide a contractor id as an argument'
            self.assertContains(str(cm.exception), error)

    def test_incorrect_ctr_parameter(self):
        f = StringIO()

        with self.assertRaises(ImproperlyConfigured) as cm:
            call_command(IMPORT_COMMAND, 'wrong_ctr', stderr=f)

            error = 'The "test" contractor is unknown. Check your configuration.'
            self.assertContains(str(cm.exception), error)
