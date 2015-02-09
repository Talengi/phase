# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase

from mock import patch

from trsimports.models import TrsImport
from trsimports.reports import ErrorReport


class ErrorReportTests(TestCase):

    def setUp(self):
        self.trs_import = TrsImport(
            trs_dir='/tmp/dummy_dir',
            tobechecked_dir='/tmp/dummy_dir',
            accepted_dir='/tmp/dummy_dir',
            rejected_dir='/tmp/dummy_dir',
            email_list=['test1@phase.fr', 'test2@phase.fr']
        )
        self.trs_import._errors = {
            'error1': 'This is error 1',
            'error2': 'This is error 2',
        }
        self.report = ErrorReport(self.trs_import)

    @patch('trsimports.reports.send_mail')
    def test_send_report(self, send_mail):
        self.report.send()
        self.assertEqual(send_mail.call_count, 1)
