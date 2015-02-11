# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase

from mock import patch

from trsimports.models import TrsImport
from trsimports.reports import ErrorReport


class ErrorReportTests(TestCase):

    def setUp(self):
        self.trs_import = TrsImport(
            trs_dir='/tmp/dummy_dir/FAC10005-CTR-CLT-TRS-00001',
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
    def test_report_is_sent(self, send_mail):
        self.report.send()
        self.assertEqual(send_mail.call_count, 1)

    def test_error_report_content(self):
        body = self.report.get_body()
        self.assertEqual(body.count('FAC10005-CTR-CLT-TRS-00001'), 1)
        self.assertEqual(body.count('This is error 1'), 1)
        self.assertEqual(body.count('This is error 2'), 1)
