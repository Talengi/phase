# -*- coding: utf-8 -*-


from django.test import TestCase, override_settings
from django.http import Http404, HttpResponse
from django.core.files.uploadedfile import SimpleUploadedFile

from privatemedia.views import serve_model_file_field
from accounts.factories import UserFactory
from categories.factories import CategoryFactory
from documents.factories import DocumentFactory


@override_settings(USE_X_SENDFILE=True)
class PrivateMediaViewTests(TestCase):
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

        sample_path = b'documents/tests/'
        pdf_doc = b'sample_doc_pdf.pdf'
        self.sample_pdf = SimpleUploadedFile(pdf_doc, sample_path + pdf_doc)

    def test_serve_wrong_field(self):
        with self.assertRaises(Http404):
            serve_model_file_field(self.rev, 'i_do_not_exist')

    def test_serve_empty_field(self):
        with self.assertRaises(Http404):
            serve_model_file_field(self.rev, 'pdf_file')

    def test_serve_file_field(self):
        self.rev.pdf_file = self.sample_pdf
        self.rev.save()

        res = serve_model_file_field(self.rev, 'pdf_file')
        self.assertTrue(isinstance(res, HttpResponse))
        self.assertTrue('X-Accel-Redirect' in res)
