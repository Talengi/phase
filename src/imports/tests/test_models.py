from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from documents.models import Document
from accounts.factories import UserFactory
from default_documents.models import DemoMetadataRevision
from categories.factories import CategoryFactory
from imports.models import ImportBatch, Import


class ImportTests(TestCase):

    def setUp(self):
        sample_path = 'imports/tests/'
        csv_file = 'demo_import_file.csv'
        f = open(sample_path + csv_file, 'rb')
        self.file = SimpleUploadedFile(csv_file, f.read())
        self.category = CategoryFactory()
        self.user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category
        )
        data = {
            'category': self.category,
            'file': self.file,
        }
        self.batch = ImportBatch.objects.create(**data)

    def test_batch_iter(self):
        rows = [row.data for row in self.batch]
        self.assertEqual(rows, [
            {
                'document_key': 'toto',
                'title': 'doc-toto',
                'status': 'STD',
                'docclass': '1',
                'received_date': '2015-10-10',
            },
            {
                'document_key': 'tata',
                'title': 'doc-tata',
                'status': 'FIN',
                'docclass': '2',
                'received_date': '2015-10-10',
            }
        ])

    def test_import(self):
        data = {
            'document_key': 'toto',
            'title': 'doc-toto',
            'status': 'STD',
            'docclass': '1',
            'created_on': '2015-10-10',
            'received_date': '2015-10-10',
        }
        imp = Import(batch=self.batch, data=data)
        imp.do_import(line=1)
        imp.save()

        self.assertEqual(imp.status, 'success')
        imp = Import.objects.get(pk=imp.pk)
        self.assertEqual(imp.document.document_key, 'toto')

    def test_failure_import(self):
        """The required "docclass" field is missing."""
        data = {
            'document_key': 'toto',
            'title': 'doc-toto',
            'status': 'STD',
        }
        imp = Import(batch=self.batch, data=data)
        imp.do_import(line=1)
        imp.save()

        self.assertEqual(imp.status, 'error')

    def test_import_multiple_revisions(self):
        data = {
            'document_key': 'toto',
            'title': 'doc-toto',
            'status': 'STD',
            'docclass': '1',
            'created_on': '2015-10-10',
            'received_date': '2015-10-10',
        }
        imp = Import(batch=self.batch, data=data)
        imp.do_import(line=1)
        imp.save()

        revisions = DemoMetadataRevision.objects \
            .filter(metadata__document__document_key='toto')
        self.assertEqual(revisions.count(), 1)

        # Importing other revisions
        data = {
            'document_key': 'toto',
            'title': 'doc-toto',
            'status': 'IDC',
            'docclass': '2',
            'created_on': '2015-10-10',
            'received_date': '2015-10-10',
        }
        imp = Import(batch=self.batch, data=data)
        imp.do_import(line=2)
        imp.save()

        data = {
            'document_key': 'toto',
            'title': 'doc-toto',
            'status': 'IFA',
            'docclass': '3',
            'created_on': '2015-10-10',
            'received_date': '2015-10-10',
        }
        imp = Import(batch=self.batch, data=data)
        imp.do_import(line=2)
        imp.save()

        revisions = DemoMetadataRevision.objects \
            .filter(metadata__document__document_key='toto')
        self.assertEqual(revisions.count(), 3)

    def test_import_multiple_revisions_updates_document_fields(self):
        data = {
            'document_key': 'toto',
            'title': 'doc-toto',
            'status': 'STD',
            'docclass': '1',
            'created_on': '2015-10-10',
            'received_date': '2015-10-10',
        }
        imp = Import(batch=self.batch, data=data)
        imp.do_import(line=1)
        imp.save()

        data = {
            'document_key': 'toto',
            'title': 'doc-tata',
            'status': 'IDC',
            'docclass': '1',
            'created_on': '2015-10-10',
            'received_date': '2015-10-10',
        }
        imp = Import(batch=self.batch, data=data)
        imp.do_import(line=2)
        imp.save()

        doc = Document.objects.get(document_key='toto')
        self.assertEqual(doc.title, 'doc-tata')

    def test_import_can_update_revision_fields(self):
        data = {
            'document_key': 'toto',
            'title': 'doc-toto',
            'status': 'STD',
            'docclass': '1',
            'created_on': '2015-10-10',
            'received_date': '2015-10-10',
        }
        imp = Import(batch=self.batch, data=data)
        imp.do_import(line=1)
        imp.save()

        data = {
            'document_key': 'toto',
            'title': 'doc-tata',
            'revision': '0',
            'status': 'IDC',
            'docclass': '2',
            'created_on': '2015-10-10',
            'received_date': '2015-10-10',
        }
        imp = Import(batch=self.batch, data=data)
        imp.do_import(line=2)
        imp.save()

        doc = Document.objects.get(document_key='toto')
        self.assertEqual(doc.current_revision, 0)
        self.assertEqual(doc.latest_revision.docclass, 2)


class ExcelTests(TestCase):

    def setUp(self):
        sample_path = 'imports/tests/'
        csv_file = 'demo_import_file.xlsx'
        f = open(sample_path + csv_file, 'rb')
        self.file = SimpleUploadedFile(csv_file, f.read())
        self.category = CategoryFactory()
        self.user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category
        )
        data = {
            'category': self.category,
            'file': self.file,
        }
        self.batch = ImportBatch.objects.create(**data)

    def test_import(self):
        self.assertEqual(Document.objects.all().count(), 0)

        self.batch.do_import()
        self.assertEqual(Document.objects.all().count(), 1)
        self.assertEqual(DemoMetadataRevision.objects.all().count(), 2)
