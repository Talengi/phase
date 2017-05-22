# -*- coding: utf-8 -*-



from django.test import TestCase

from mock import patch

from categories.factories import CategoryFactory
from transmittals.imports import TrsImport
from transmittals.reports import ErrorReport


class ErrorReportTests(TestCase):

    def setUp(self):
        self.trs_import = TrsImport(
            trs_dir='/tmp/dummy_dir/FAC10005-CTR-CLT-TRS-00001',
            tobechecked_dir='/tmp/dummy_dir',
            accepted_dir='/tmp/dummy_dir',
            rejected_dir='/tmp/dummy_dir',
            email_list=['test1@phase.fr', 'test2@phase.fr'],
            contractor='dummy_dir',
            doc_category=CategoryFactory(),
            trs_category=CategoryFactory(),
        )
        self.trs_import._errors = {
            'error1': 'This is error 1',
            'error2': 'This is error 2',
        }
        self.report = ErrorReport(self.trs_import)

    @patch('transmittals.reports.send_mail')
    def test_report_is_sent(self, send_mail):
        self.report.send()
        self.assertEqual(send_mail.call_count, 1)

    def test_error_report_content(self):
        subject = self.report.get_subject()
        self.assertEqual(subject.count('FAC10005-CTR-CLT-TRS-00001'), 1)

        body = self.report.get_body()
        self.assertEqual(body.count('This is error 1'), 1)
        self.assertEqual(body.count('This is error 2'), 1)
