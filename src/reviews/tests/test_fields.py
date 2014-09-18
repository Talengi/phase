import os

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from categories.factories import CategoryFactory
from accounts.factories import UserFactory
from documents.factories import DocumentFactory
from reviews.models import Review


class FieldTests(TestCase):

    def setUp(self):
        self.category = CategoryFactory()
        self.user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category
        )
        self.doc = DocumentFactory(
            document_key=u'HAZOP-related',
            category=self.category
        )

    def tearDown(self):
        """Wipe the media root directory after each test."""
        media_root = settings.MEDIA_ROOT
        if os.path.exists(media_root):
            for f in os.listdir(media_root):
                file_path = os.path.join(media_root, f)
                if os.path.isfile(file_path) and file_path.startswith('/tmp/'):
                    os.unlink(file_path)

    def test_reviewer_comment_file_name(self):
        """Test that comment files are renamed correctly."""
        sample_path = 'documents/tests/'
        sample_file = 'sample_doc_zip.zip'

        review = Review.objects.create(
            reviewer=self.user,
            role='reviewer',
            document=self.doc,
            revision=self.doc.current_revision,
            comments=SimpleUploadedFile(sample_file, sample_path + sample_file),
        )

        self.assertEqual(
            review.comments.name,
            u'HAZOP-related_01_4_comments.zip'
        )

    def test_leader_comment_file_name(self):
        """Test that comment files are renamed correctly."""
        sample_path = 'documents/tests/'
        sample_file = 'sample_doc_zip.zip'

        review = Review.objects.create(
            reviewer=self.user,
            role='leader',
            document=self.doc,
            revision=self.doc.current_revision,
            comments=SimpleUploadedFile(sample_file, sample_path + sample_file),
        )

        self.assertEqual(
            review.comments.name,
            u'HAZOP-related_01_leader_comments.zip'
        )

    def test_approver_comment_file_name(self):
        """Test that comment files are renamed correctly."""
        sample_path = 'documents/tests/'
        sample_file = 'sample_doc_zip.zip'

        review = Review.objects.create(
            reviewer=self.user,
            role='approver',
            document=self.doc,
            revision=self.doc.current_revision,
            comments=SimpleUploadedFile(sample_file, sample_path + sample_file),
        )

        self.assertEqual(
            review.comments.name,
            u'HAZOP-related_01_GTG_comments.zip'
        )
