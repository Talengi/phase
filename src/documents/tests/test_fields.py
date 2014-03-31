import os

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from categories.factories import CategoryFactory
from documents.factories import DocumentFactory


class FieldTests(TestCase):

    def setUp(self):
        self.category = CategoryFactory()

    def tearDown(self):
        """Wipe the media root directory after each test."""
        media_root = settings.MEDIA_ROOT
        if os.path.exists(media_root):
            for f in os.listdir(media_root):
                file_path = os.path.join(media_root, f)
                if os.path.isfile(file_path) and file_path.startswith('/tmp/'):
                    os.unlink(file_path)

    def test_comment_file_fields(self):
        """Test that comment files are renamed correctly."""
        sample_path = 'documents/tests/'
        sample_file = 'sample_doc_zip.zip'

        document = DocumentFactory(
            document_key=u'HAZOP-related',
            category=self.category,
            revision={
                'leader_comments': SimpleUploadedFile(sample_file, sample_path + sample_file),
                'approver_comments': SimpleUploadedFile(sample_file, sample_path + sample_file),
            }
        )
        revision = document.metadata.latest_revision
        self.assertEqual(
            revision.leader_comments.name,
            u'HAZOP-related_1_leader_comments.zip'
        )
        self.assertEqual(
            revision.approver_comments.name,
            u'HAZOP-related_1_GTG_comments.zip'
        )
