from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.contenttypes.models import ContentType

from imports.models import ImportBatch


class ImportTests(TestCase):

    def setUp(self):
        sample_path = 'imports/tests/'
        csv_file = 'demo_import_file.csv'
        f = open(sample_path + csv_file, 'rb')
        self.file = SimpleUploadedFile(csv_file, f.read())
        self.type = ContentType.objects.get(
            app_label='default_documents',
            model='demometadata'
        )

    def test_get_columns(self):
        data = {
            'imported_type': self.type,
            'file': self.file,
        }
        batch = ImportBatch.objects.create(**data)
        rows = [row for row in batch]
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
