# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from io import BytesIO
from zipfile import ZipFile

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from accounts.factories import UserFactory
from categories.factories import CategoryFactory
from default_documents.factories import MetadataRevisionFactory
from default_documents.models import DemoMetadata, DemoMetadataRevision
from documents.factories import DocumentFactory
from documents.models import Document


class GenericViewTest(TestCase):

    def setUp(self):
        self.client = Client()

        # Login as admin by default so we won't be bothered by missing permissions
        self.category = CategoryFactory()
        user = UserFactory(email='testadmin@phase.fr', password='pass',
                           is_superuser=True,
                           category=self.category)
        self.client.login(email=user.email, password='pass')
        self.document_list_url = reverse('category_document_list', args=[
            self.category.organisation.slug,
            self.category.slug
        ])

    def assertGet(self, parameters={}, auth=None, status_code=200):
        if auth:
            response = self.client.login(**auth)
            self.assertEqual(response, True)
        response = self.client.get(self.url, parameters, follow=True)
        self.assertEqual(response.status_code, status_code)
        self.content = response.content
        self.context = response.context

    def assertPost(self, parameters={}, auth=None, status_code=200):
        if auth:
            response = self.client.login(**auth)
            self.assertEqual(response, True)
        response = self.client.post(self.url, parameters)
        self.assertEqual(response.status_code, status_code)
        self.content = response.content
        self.context = response.context

    def assertContext(self, key, value):
        self.assertTrue(key in self.context)
        self.assertEqual(self.context[key], value)

    def assertContextLength(self, key, length):
        self.assertTrue(key in self.context)
        self.assertEqual(len(self.context[key]), length)

    def assertRendering(self, needle):
        self.assertInHTML(needle, self.content)

    def assertRedirect(self, target):
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.redirect_chain, [(target, 302)])


class DocumentDetailTest(TestCase):

    def setUp(self):
        self.category = CategoryFactory()
        self.user = UserFactory(
            name='User',
            password='pass',
            is_superuser=True,
            category=self.category)
        self.client.login(username=self.user.email, password='pass')

    def test_document_number(self):
        """Tests that a document detail returns a document and his form. """
        document = DocumentFactory(
            document_key='hazop-report',
            category=self.category,
        )

        url = reverse("document_detail", args=[
            self.category.organisation.slug,
            self.category.slug,
            document.document_key
        ])
        res = self.client.get(url)
        self.assertContains(res, "hazop-report")

    def test_document_related_documents(self):
        documents = [
            DocumentFactory(document_key=u'HAZOP-related-1'),
            DocumentFactory(document_key=u'HAZOP-related-2'),
        ]
        document = DocumentFactory(
            document_key=u'HAZOP-report',
            category=self.category)
        document.metadata.related_documents = documents
        document.metadata.save()

        url = document.get_absolute_url()
        res = self.client.get(url, follow=True)
        self.assertContains(res, 'HAZOP-related-1')
        self.assertContains(res, 'HAZOP-related-2')


class DocumentDownloadTest(TestCase):

    def setUp(self):
        # Login as admin so we won't be bothered by missing permissions
        self.category = CategoryFactory()
        self.download_url = self.category.get_download_url()
        user = UserFactory(email='testadmin@phase.fr', password='pass',
                           is_superuser=True,
                           category=self.category)
        self.client.login(email=user.email, password='pass')

    def tearDown(self):
        """Wipe the media root directory after each test."""
        media_root = settings.MEDIA_ROOT
        if os.path.exists(media_root):
            for f in os.listdir(media_root):
                file_path = os.path.join(media_root, f)
                if os.path.isfile(file_path) and file_path.startswith('/tmp/'):
                    os.unlink(file_path)

    def test_unique_document_download(self):
        """
        Tests that a document download returns a zip file of the latest revision.
        """
        sample_path = b'documents/tests/'
        native_doc = b'sample_doc_native.docx'
        pdf_doc = b'sample_doc_pdf.pdf'

        document = DocumentFactory(
            document_key=u'HAZOP-related',
            category=self.category,
            revision={
                'native_file': SimpleUploadedFile(native_doc, sample_path + native_doc),
                'pdf_file': SimpleUploadedFile(pdf_doc, sample_path + pdf_doc),
            }
        )
        c = self.client
        r = c.post(self.download_url, {
            'document_ids': document.id,
        })
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r._headers, {
            'vary': ('Vary', 'Cookie'),
            'content-length': ('Content-Length', '398'),
            'content-type': ('Content-Type', 'application/zip'),
            'content-disposition': (
                'Content-Disposition',
                'attachment; filename=download.zip'
            )
        })

    def test_empty_document_download(self):
        """
        Tests that a document download returns an empty zip file.
        """
        document = DocumentFactory(
            document_key=u'HAZOP-related',
            category=self.category,
        )
        r = self.client.post(self.download_url, {'document_ids': [document.id]})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r._headers, {
            'content-length': ('Content-Length', '22'),
            'content-type': ('Content-Type', 'application/zip'),
            'vary': ('Vary', 'Cookie'),
            'content-disposition': (
                'Content-Disposition',
                'attachment; filename=download.zip'
            )
        })

    def test_multiple_document_download(self):
        """
        Tests that download returns a zip file of the latest revision
        of all documents.
        """
        sample_path = b'documents/tests/'
        native_doc = b'sample_doc_native.docx'
        pdf_doc = b'sample_doc_pdf.pdf'

        document1 = DocumentFactory(
            document_key=u'HAZOP-related',
            category=self.category,
            revision={
                'native_file': SimpleUploadedFile(native_doc, sample_path + native_doc),
                'pdf_file': SimpleUploadedFile(pdf_doc, sample_path + pdf_doc),
            }
        )

        document2 = DocumentFactory(
            document_key=u'HAZOP-related-2',
            category=self.category,
            revision={
                'native_file': SimpleUploadedFile(native_doc, sample_path + native_doc),
                'pdf_file': SimpleUploadedFile(pdf_doc, sample_path + pdf_doc),
            }
        )
        r = self.client.post(self.download_url, {
            'document_ids': [
                document1.id,
                document2.id,
            ],
        })
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r._headers, {
            'vary': ('Vary', 'Cookie'),
            'content-length': ('Content-Length', '782'),
            'content-type': ('Content-Type', 'application/zip'),
            'content-disposition': (
                'Content-Disposition',
                'attachment; filename=download.zip'
            )
        })

    def test_multiple_pdf_document_download(self):
        """
        Tests that download returns a zip file of the latest revision
        of pdf documents.
        """
        sample_path = b'documents/tests/'
        native_doc = b'sample_doc_native.docx'
        pdf_doc = b'sample_doc_pdf.pdf'

        document1 = DocumentFactory(
            document_key=u'HAZOP-related',
            category=self.category,
            revision={
                'native_file': SimpleUploadedFile(native_doc, sample_path + native_doc),
                'pdf_file': SimpleUploadedFile(pdf_doc, sample_path + pdf_doc),
            }
        )

        document2 = DocumentFactory(
            document_key=u'HAZOP-related-2',
            category=self.category,
            revision={
                'native_file': SimpleUploadedFile(native_doc, sample_path + native_doc),
                'pdf_file': SimpleUploadedFile(pdf_doc, sample_path + pdf_doc),
            }
        )
        c = self.client
        r = c.post(self.download_url, {
            'document_ids': [
                document1.id,
                document2.id,
            ],
            'format': 'pdf',
        })
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r._headers, {
            'vary': ('Vary', 'Cookie'),
            'content-length': ('Content-Length', '396'),
            'content-type': ('Content-Type', 'application/zip'),
            'content-disposition': (
                'Content-Disposition',
                'attachment; filename=download.zip'
            )
        })

    def test_all_revisions_document_download(self):
        """
        Tests that download returns a zip file of all revisions
        of a document.
        """
        document = DocumentFactory(
            category=self.category,
        )
        sample_path = b'documents/tests/'
        native_doc = b'sample_doc_native.docx'
        pdf_doc = b'sample_doc_pdf.pdf'

        MetadataRevisionFactory(
            document=document,
            revision=2,
            native_file=SimpleUploadedFile(native_doc, sample_path + native_doc),
            pdf_file=SimpleUploadedFile(pdf_doc, sample_path + pdf_doc),
        )
        MetadataRevisionFactory(
            document=document,
            revision=3,
            native_file=SimpleUploadedFile(native_doc, sample_path + native_doc),
            pdf_file=SimpleUploadedFile(pdf_doc, sample_path + pdf_doc),
        )
        r = self.client.post(document.category.get_download_url(), {
            'document_ids': document.id,
            'revisions': 'all',
        })
        self.assertEqual(r.status_code, 200)

        zipfile = BytesIO(r.content)
        filelist = ZipFile(zipfile).namelist()
        self.assertEqual(len(filelist), 4)


class DocumentReviseTests(TestCase):

    def setUp(self):
        self.category = CategoryFactory()
        user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category,
        )
        self.client.login(email=user.email, password='pass')

    def test_cannot_revise_document_in_review(self):
        document = DocumentFactory(
            category=self.category,
            document_key='FAC09001-FWF-000-HSE-REP-0004',
            revision={
                'status': 'STD',
                'review_start_date': '2014-04-04'
            }
        )
        revision = document.latest_revision
        self.assertTrue(revision.is_under_review)

        url = reverse('document_revise', args=[
            self.category.organisation.slug,
            self.category.slug,
            document.document_key
        ])

        res = self.client.get(url)
        self.assertEqual(res.status_code, 403)


class DocumentDeleteTests(TestCase):

    def setUp(self):
        self.category = CategoryFactory()
        user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category,
        )
        self.client.login(email=user.email, password='pass')
        self.doc_list_url = self.category.get_absolute_url()

    def test_delete_page_only_post(self):
        document = DocumentFactory(category=self.category)
        delete_url = reverse('document_delete', args=[
            self.category.organisation.slug,
            self.category.slug,
            document.document_key
        ])
        res = self.client.get(delete_url)
        self.assertEqual(res.status_code, 405)

    def test_delete_document(self):
        document = DocumentFactory(category=self.category)
        delete_url = reverse('document_delete', args=[
            self.category.organisation.slug,
            self.category.slug,
            document.document_key
        ])
        res = self.client.post(delete_url)
        self.assertRedirects(res, self.category.get_absolute_url())

        res = self.client.post(delete_url)
        self.assertEqual(res.status_code, 404)

        metadata = DemoMetadata.objects.filter(document=document)
        self.assertEqual(metadata.count(), 0)

        revisions = DemoMetadataRevision.objects.filter(document=document)
        self.assertEqual(revisions.count(), 0)

    def test_cannot_revise_document_in_review(self):
        document = DocumentFactory(
            category=self.category,
            document_key='FAC09001-FWF-000-HSE-REP-0004',
            revision={
                'status': 'STD',
                'review_start_date': '2014-04-04'
            }
        )
        delete_url = reverse('document_delete', args=[
            self.category.organisation.slug,
            self.category.slug,
            document.document_key
        ])

        revision = document.latest_revision
        self.assertTrue(revision.is_under_review)

        res = self.client.post(delete_url)
        self.assertEqual(res.status_code, 403)

        try:
            document = Document.objects.get(document_key=document.document_key)
        except:
            self.fail('Document was deleted')

    def test_simple_user_cannot_delete_document(self):
        user = UserFactory(
            email='testuser@phase.fr',
            password='pass',
            is_superuser=False,
            category=self.category,
        )

        self.client.login(email=user.email, password='pass')
        document = DocumentFactory(category=self.category)
        delete_url = reverse('document_delete', args=[
            self.category.organisation.slug,
            self.category.slug,
            document.document_key
        ])

        res = self.client.post(delete_url)

        self.assertEqual(res.status_code, 403)
