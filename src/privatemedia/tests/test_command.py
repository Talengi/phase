# -*- coding: utf-8 -*-


import os

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings

from accounts.factories import UserFactory
from categories.factories import CategoryFactory
from default_documents.factories import MetadataRevisionFactory
from documents.factories import DocumentFactory


@override_settings(USE_X_SENDFILE=True)
class CleanMediaTests(TestCase):
    def setUp(self):
        self.category = CategoryFactory()
        user = UserFactory(
            email='test@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category)
        self.client.login(email=user.email, password='pass')
        self.doc = DocumentFactory()
        self.rev = self.doc.get_latest_revision()

    def test_command(self):
        document = DocumentFactory(
            category=self.category,
        )
        native_doc = 'sample_doc_native.docx'
        pdf_doc = 'sample_doc_pdf.pdf'

        MetadataRevisionFactory(
            metadata=document.get_metadata(),
            revision=2,
            native_file=SimpleUploadedFile(native_doc, b'content'),
            pdf_file=SimpleUploadedFile(pdf_doc, b'content'),
        )
        # Document without files
        DocumentFactory(
            category=self.category,
        )
        rev = document.get_latest_revision()
        filepath = rev.pdf_file.path
        # check file is on disk after doc deletion
        document.delete()
        self.assertTrue(os.path.exists(filepath))

        call_command('clearmedia')
        # command has deleted file
        self.assertFalse(os.path.exists(filepath))
