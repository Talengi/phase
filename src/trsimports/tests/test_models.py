# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
from os.path import join
import tempfile
from shutil import rmtree, copytree

from django.test import TestCase
from django.contrib.contenttypes.models import ContentType

from categories.factories import CategoryFactory
from documents.factories import DocumentFactory
from default_documents.models import ContractorDeliverable
from default_documents.factories import (
    ContractorDeliverableFactory, ContractorDeliverableRevisionFactory)
from trsimports.models import TrsImport


TEST_CTR = 'test'


class TransmittalsValidationTests(TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix='phasetest_', suffix='_trs')
        incoming = join(self.tmpdir, 'incoming')
        tobechecked = join(self.tmpdir, 'tobechecked')
        accepted = join(self.tmpdir, 'accepted')
        rejected = join(self.tmpdir, 'rejected')

        os.mkdir(accepted)
        os.mkdir(rejected)
        os.mkdir(tobechecked)

        self.config = {
            'INCOMING_DIR': incoming,
            'REJECTED_DIR': rejected,
            'TO_BE_CHECKED_DIR': tobechecked,
            'ACCEPTED_DIR': accepted,
        }

        ContractorDeliverableModel = ContentType.objects.get_for_model(ContractorDeliverable)
        category = CategoryFactory(category_template__metadata_model=ContractorDeliverableModel)
        DocumentFactory(
            document_key='FAC10005-CTR-000-EXP-LAY-0000',
            category=category,
            metadata_factory_class=ContractorDeliverableFactory,
            revision_factory_class=ContractorDeliverableRevisionFactory,
        )

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
        )
        return trs_import


class DirectoryContentTests(TransmittalsValidationTests):

    def test_invalid_directory_name(self):
        trs_import = self.prepare_fixtures('invalid_trs_dirname', 'I-Love-Bananas')
        self.assertTrue('invalid_dirname' in trs_import.errors['global_errors'])

    def test_missing_csv(self):
        trs_import = self.prepare_fixtures('missing_csv', 'FAC10005-CTR-CLT-TRS-00001')
        self.assertTrue('missing_csv' in trs_import.errors['global_errors'])

    def test_wrong_csv_filename(self):
        trs_import = self.prepare_fixtures('wrong_csv_filename', 'FAC10005-CTR-CLT-TRS-00001')
        self.assertTrue('missing_csv' in trs_import.errors['global_errors'])

    def test_not_enough_pdfs(self):
        trs_import = self.prepare_fixtures('not_enough_pdfs', 'FAC10005-CTR-CLT-TRS-00001')
        self.assertTrue('wrong_pdf_count' in trs_import.errors['global_errors'])

    def test_too_many_pdfs(self):
        trs_import = self.prepare_fixtures('too_many_pdfs', 'FAC10005-CTR-CLT-TRS-00001')
        self.assertTrue('wrong_pdf_count' in trs_import.errors['global_errors'])


class CSVContentTests(TransmittalsValidationTests):

    def test_missing_csv_data(self):
        trs_import = self.prepare_fixtures('missing_data', 'FAC10005-CTR-CLT-TRS-00001')
        self.assertTrue('missing_data' in trs_import.errors['csv_content'][2])

    def test_missing_document(self):
        trs_import = self.prepare_fixtures('missing_document', 'FAC10005-CTR-CLT-TRS-00001')
        self.assertTrue('document_not_found' in trs_import.errors['csv_content'][2])

    def test_missing_pdf_file(self):
        trs_import = self.prepare_fixtures('missing_pdf', 'FAC10005-CTR-CLT-TRS-00001')
        self.assertTrue('missing_pdf' in trs_import.errors['csv_content'][2])
