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
            },
            {
                'document_key': 'tata',
                'title': 'doc-tata',
                'status': 'FIN',
            }
        ])

    def test_import(self):
        data = {
            'document_key': 'toto',
            'title': 'doc-toto',
            'status': 'STD',
        }
        imp = Import(batch=self.batch, data=data)
        imp.do_import()
