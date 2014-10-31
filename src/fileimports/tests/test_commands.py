# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from io import StringIO

from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError


IMPORT_COMMAND = 'import_revision_files'


class ImportCommandTests(TestCase):

    def test_directory_does_not_exist(self):
        import_dir = '/i/do/not/exist/'
        with self.settings(IMPORT_ROOT=import_dir):
            f = StringIO()
            with self.assertRaises(CommandError) as cm:
                call_command(IMPORT_COMMAND, stderr=f)

            error = 'The directory "/i/do/not/exist/" does not exist'
            self.assertEqual(str(cm.exception), error)
