from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from documents.models import Document
from documents.factories import DocumentFactory
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
                'klass': '1',
            },
            {
                'document_key': 'tata',
                'title': 'doc-tata',
                'status': 'FIN',
                'klass': '2',
            }
        ])

    def test_import(self):
        data = {
            'document_key': 'toto',
            'title': 'doc-toto',
            'status': 'STD',
            'klass': '1',
        }
        imp = Import(batch=self.batch, data=data)
        imp.do_import(line=1)
        imp.save()

        self.assertEqual(imp.status, 'success')
        imp = Import.objects.get(pk=imp.pk)
        self.assertEqual(imp.document.document_key, 'toto')

    def test_failure_import(self):
        """The required "klass" field is missing."""
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
            'klass': '1',
        }
        imp = Import(batch=self.batch, data=data)
        imp.do_import(line=1)
        imp.save()

        revisions = DemoMetadataRevision.objects \
            .filter(document__document_key='toto')
        self.assertEqual(revisions.count(), 1)

        # Importing other revisions
        data = {
            'document_key': 'toto',
            'title': 'doc-toto',
            'status': 'IDC',
            'klass': '2',
        }
        imp = Import(batch=self.batch, data=data)
        imp.do_import(line=2)
        imp.save()

        data = {
            'document_key': 'toto',
            'title': 'doc-toto',
            'status': 'IFA',
            'klass': '3',
        }
        imp = Import(batch=self.batch, data=data)
        imp.do_import(line=2)
        imp.save()

        revisions = DemoMetadataRevision.objects \
            .filter(document__document_key='toto')
        self.assertEqual(revisions.count(), 3)

    def test_import_multiple_revisions_updates_document_fields(self):
        data = {
            'document_key': 'toto',
            'title': 'doc-toto',
            'status': 'STD',
            'klass': '1',
        }
        imp = Import(batch=self.batch, data=data)
        imp.do_import(line=1)
        imp.save()

        data = {
            'document_key': 'toto',
            'title': 'doc-tata',
            'status': 'IDC',
            'klass': '1',
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
            'klass': '1',
        }
        imp = Import(batch=self.batch, data=data)
        imp.do_import(line=1)
        imp.save()

        data = {
            'document_key': 'toto',
            'title': 'doc-tata',
            'revision': '0',
            'status': 'IDC',
            'klass': '2',
        }
        imp = Import(batch=self.batch, data=data)
        imp.do_import(line=2)
        imp.save()

        doc = Document.objects.get(document_key='toto')
        self.assertEqual(doc.current_revision, 0)
        self.assertEqual(doc.latest_revision.klass, 2)

    def test_import_revision_document_under_review(self):
        """Documents under review cannot be revised"""
        doc = DocumentFactory(
            document_key='toto',
            category=self.category,
            revision={
                'reviewers': [self.user],
                'leader': self.user,
                'approver': self.user,
            }
        )
        doc.latest_revision.start_review()
        self.assertTrue(doc.latest_revision.is_under_review())

        data = {
            'document_key': 'toto',
            'title': 'New title',
            'status': 'IDC',
            'klass': '1',
        }
        imp = Import(batch=self.batch, data=data)
        imp.do_import(line=2)
        imp.save()

        self.assertEqual(imp.status, 'error')


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
