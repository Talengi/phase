# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase

from trsimports.tasks import revfile_re


class ImportFileTests(TestCase):

    def test_wrong_files_regex(self):
        wrong_names = [
            'toto',
            'toto.pdf',
            'toto.tata.pdf',
            'FAC09001-CTR',
            'FAC09001-CTR.pdf',
            'FAC09001-CTR.pdf',
            'FAC09001-CTR-3.pdf',
            'FAC09001-CTR-03.pdf',
            'FAC09001_CTR-03.pdf',
            '03.pdf',
        ]
        for name in wrong_names:
            self.assertIsNone(revfile_re.match(name))

    def test_correct_files_regex(self):
        names = [
            'toto_1.pdf',
            'toto_01.pdf',
            'toto_0001.pdf',
            'toto_42.pdf',
            'toto_042.pdf',
            'FAC09001-CTR-000-MAI-SCH-6063_03.docx'
        ]
        for name in names:
            self.assertIsNotNone(revfile_re.match(name))
