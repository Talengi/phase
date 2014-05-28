from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from categories.factories import CategoryFactory
from imports.models import ImportBatch, Import


class ImportTests(TestCase):

    def setUp(self):
        sample_path = 'imports/tests/'
        csv_file = 'demo_import_file.csv'
        f = open(sample_path + csv_file, 'rb')
        self.file = SimpleUploadedFile(csv_file, f.read())
        category = CategoryFactory()
        data = {
            'category': category,
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
        imp.do_import()
        imp.save()

        self.assertEqual(imp.status, 'success')
        imp = Import.objects.get(pk=imp.pk)
        self.assertEqual(imp.document.document_key, 'toto')
        self.assertEqual(imp.document.status, 1)

    def test_failure_import(self):
        data = {
            'document_key': 'toto',
            'title': 'doc-toto',
            'status': 'STD',
        }
        imp = Import(batch=self.batch, data=data)
        imp.do_import()
        imp.save()

        self.assertEqual(imp.status, 'error')
