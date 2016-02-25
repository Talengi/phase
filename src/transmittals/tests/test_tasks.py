# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
from os.path import join
import tempfile

from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile

from documents.factories import DocumentFactory
from categories.factories import CategoryFactory
from default_documents.factories import (
    ContractorDeliverableFactory, ContractorDeliverableRevisionFactory)
from default_documents.models import ContractorDeliverable
from transmittals.factories import TransmittalFactory, TrsRevisionFactory
from transmittals.tasks import process_transmittal


def touch(path):
    """Simply creates an empty file."""
    open(path, 'a').close()


class ProcessTransmittalTests(TestCase):
    fixtures = ['initial_values_lists']

    def setUp(self):
        # Filesystem setup
        self.tmpdir = tempfile.mkdtemp(prefix='phasetest_', suffix='_trs')
        self.incoming = join(self.tmpdir, 'incoming')
        self.tobechecked = join(self.tmpdir, 'tobechecked')
        self.accepted = join(self.tmpdir, 'accepted')
        self.rejected = join(self.tmpdir, 'rejected')

        os.mkdir(self.accepted)
        os.mkdir(self.rejected)
        os.mkdir(self.tobechecked)

        Model = ContentType.objects.get_for_model(ContractorDeliverable)
        self.category = CategoryFactory(category_template__metadata_model=Model)
        self.document = DocumentFactory(
            document_key='FAC10005-CTR-000-EXP-LAY-4891',
            latest_revision=2,
            metadata={
                'title': 'Cause & Effect Chart',
                'contract_number': 'FAC10005',
                'originator': 'CTR',
                'unit': '000',
                'discipline': 'EXP',
                'document_type': 'LAY',
                'sequential_number': '4891',
            },
            revision={
                'revision': 1,
                'docclass': 1,
                'status': 'SPD',
            },
            metadata_factory_class=ContractorDeliverableFactory,
            revision_factory_class=ContractorDeliverableRevisionFactory,
            category=self.category)
        self.metadata = self.document.metadata

        ContractorDeliverableRevisionFactory(
            metadata=self.metadata,
            revision=2,
            docclass=1,
            status='SPD')

        sample_path = b'documents/tests/'
        native_doc = b'sample_doc_native.docx'
        pdf_doc = b'sample_doc_pdf.pdf'

        self.transmittal = TransmittalFactory(
            document_key='FAC10005-CTR-CLT-TRS-00001',
            status='tobechecked',
            tobechecked_dir=self.tobechecked,
            accepted_dir=self.accepted,
            rejected_dir=self.rejected,
            contractor='test')
        os.mkdir(self.transmittal.full_tobechecked_name)

        data = {
            'transmittal': self.transmittal,
            'document': self.document,
            'category': self.category,
            'title': 'Cause & Effect Chart',
            'contract_number': 'FAC10005',
            'originator': 'CTR',
            'unit': '000',
            'discipline': 'EXP',
            'document_type': 'LAY',
            'sequential_number': '4891',
            'docclass': 1,
            'revision': 1,
            'status': 'SPD',
            'pdf_file': SimpleUploadedFile(pdf_doc, sample_path + pdf_doc),
            'created_on': '2015-10-10',
        }
        TrsRevisionFactory(**data)

        data.update({'revision': 2, 'status': 'IFA'})
        TrsRevisionFactory(**data)

        data.update({'revision': 3, 'docclass': 2})
        TrsRevisionFactory(**data)

        data.update({
            'revision': 4,
            'status': 'FIN',
            'native_file': SimpleUploadedFile(native_doc, sample_path + native_doc),
        })
        TrsRevisionFactory(**data)

    def test_process_update_revisions(self):
        rev = self.document.metadata.get_revision(2)
        self.assertEqual(rev.status, 'SPD')
        process_transmittal(self.transmittal.pk)

        rev = self.document.metadata.get_revision(2)
        self.assertEqual(rev.status, 'IFA')

    def test_process_create_revisions(self):
        rev = self.document.metadata.get_revision(3)
        self.assertIsNone(rev)

        process_transmittal(self.transmittal.pk)

        rev = self.document.metadata.get_revision(3)
        self.assertIsNotNone(rev)
        self.assertEqual(rev.status, 'IFA')

        rev = self.document.metadata.get_revision(4)
        self.assertIsNotNone(rev)
        self.assertEqual(rev.status, 'FIN')

    def test_process_updates_files(self):
        rev = self.document.metadata.get_revision(1)
        self.assertFalse(rev.pdf_file)

        process_transmittal(self.transmittal.pk)

        rev = self.document.metadata.get_revision(1)
        self.assertTrue(rev.pdf_file)

        rev = self.document.metadata.get_revision(3)
        self.assertTrue(rev.pdf_file)
        self.assertFalse(rev.native_file)

        rev = self.document.metadata.get_revision(4)
        self.assertTrue(rev.pdf_file)
        self.assertTrue(rev.native_file)

    def test_successfull_process_moves_files_to_accepted_dir(self):
        tobechecked_file = join(self.transmittal.full_tobechecked_name, 'toto.csv')
        accepted_file = join(self.transmittal.full_accepted_name, 'toto.csv')

        touch(tobechecked_file)

        self.assertTrue(os.path.exists(tobechecked_file))
        self.assertFalse(os.path.exists(accepted_file))

        process_transmittal(self.transmittal.pk)

        self.assertFalse(os.path.exists(tobechecked_file))
        self.assertTrue(os.path.exists(accepted_file))
