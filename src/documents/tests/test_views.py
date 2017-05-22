# -*- coding: utf-8 -*-


import os
from io import BytesIO
from zipfile import ZipFile

from django.conf import settings
from django.contrib.auth.models import Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings
from django.test.client import Client

from accounts.factories import UserFactory
from audit_trail.models import Activity
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

    def assertGet(self, parameters=None, auth=None, status_code=200):
        if not parameters:
            parameters = {}
        if auth:
            response = self.client.login(**auth)
            self.assertEqual(response, True)
        response = self.client.get(self.url, parameters, follow=True)
        self.assertEqual(response.status_code, status_code)
        self.content = response.content
        self.context = response.context

    def assertPost(self, parameters=None, auth=None, status_code=200):
        if not parameters:
            parameters = {}
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
            DocumentFactory(document_key='HAZOP-related-1'),
            DocumentFactory(document_key='HAZOP-related-2'),
        ]
        document = DocumentFactory(
            document_key='HAZOP-report',
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
        self.maxDiff = None

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
        native_doc = b'sample_doc_native.docx'
        pdf_doc = b'sample_doc_pdf.pdf'

        document = DocumentFactory(
            document_key='HAZOP-related',
            category=self.category,
            revision={
                'native_file': SimpleUploadedFile(native_doc, b'content'),
                'pdf_file': SimpleUploadedFile(pdf_doc, b'content'),
            }
        )
        c = self.client
        r = c.post(self.download_url, {
            'document_ids': document.id,
            'revisions': 'latest',
            'format': 'both',
        })
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r._headers['vary'],
                         ('Vary', 'Cookie, Accept-Encoding'))
        self.assertEqual(r._headers['content-type'],
                         ('Content-Type', 'application/zip'))
        self.assertEqual(r._headers['content-disposition'], (
            'Content-Disposition',
            'attachment; filename=download.zip'))

    def test_empty_document_download(self):
        """
        Tests that a document download returns an empty zip file.
        """
        document = DocumentFactory(
            document_key='HAZOP-related',
            category=self.category,
        )
        r = self.client.post(self.download_url, {
            'document_ids': [document.id],
            'revisions': 'latest',
            'format': 'both',
        })
        self.assertEqual(r.status_code, 200)
        self.assertDictEqual(r._headers, {
            'content-length': ('Content-Length', '22'),
            'content-language': ('Content-Language', 'en'),
            'content-type': ('Content-Type', 'application/zip'),
            'vary': ('Vary', 'Accept-Language, Cookie'),
            'x-frame-options': ('X-Frame-Options', 'SAMEORIGIN'),
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
        native_doc = 'sample_doc_native.docx'
        pdf_doc = 'sample_doc_pdf.pdf'

        MetadataRevisionFactory(
            metadata=document.get_metadata(),
            revision=2,
            native_file=SimpleUploadedFile(native_doc, b'content'),
            pdf_file=SimpleUploadedFile(pdf_doc, b'content'),
        )
        MetadataRevisionFactory(
            metadata=document.get_metadata(),
            revision=3,
            native_file=SimpleUploadedFile(native_doc, b'content'),
            pdf_file=SimpleUploadedFile(pdf_doc, b'content'),
        )
        r = self.client.post(document.category.get_download_url(), {
            'document_ids': document.id,
            'revisions': 'all',
            'format': 'both',
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
        self.user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category,
        )
        self.client.login(email=self.user.email, password='pass')
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
        document_str = str(document)
        delete_url = reverse('document_delete', args=[
            self.category.organisation.slug,
            self.category.slug,
            document.document_key
        ])
        res = self.client.post(delete_url)
        self.assertRedirects(res, self.category.get_absolute_url())

        # Check that deletion was logged in audit trail
        activity = Activity.objects.latest('created_on')
        self.assertEqual(activity.verb, Activity.VERB_DELETED)
        self.assertEqual(activity.action_object_str, document_str)
        self.assertEqual(activity.actor, self.user)

        res = self.client.post(delete_url)
        self.assertEqual(res.status_code, 404)

        metadata = DemoMetadata.objects.filter(document=document)
        self.assertEqual(metadata.count(), 0)

        revisions = DemoMetadataRevision.objects.filter(metadata=metadata)
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

    def test_user_with_delete_perms_can_delete_document(self):
        user = UserFactory(
            email='testuser@phase.fr',
            password='pass',
            is_superuser=False,
            category=self.category,
        )
        delete_doc_perm = Permission.objects.get(
            codename='delete_document')
        user.user_permissions.add(delete_doc_perm)

        self.client.login(email=user.email, password='pass')
        document = DocumentFactory(category=self.category)
        delete_url = reverse('document_delete', args=[
            self.category.organisation.slug,
            self.category.slug,
            document.document_key
        ])

        res = self.client.post(delete_url)

        self.assertRedirects(res, self.category.get_absolute_url())
        self.assertFalse(Document.objects.filter(pk=document.pk).exists())


class DocumentRevisionDeleteTests(TestCase):
    def create_doc(self, nb_revisions=1):
        doc = DocumentFactory(category=self.category)
        meta = doc.get_metadata()
        for rev in range(2, nb_revisions + 1):
            MetadataRevisionFactory(
                metadata=meta,
                revision=rev
            )
        url = reverse('document_revision_delete', args=[
            self.category.organisation.slug,
            self.category.slug,
            doc.document_key
        ])
        return doc, url

    def setUp(self):
        self.category = CategoryFactory()
        self.user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category,
        )
        self.client.login(email=self.user.email, password='pass')
        self.doc_list_url = self.category.get_absolute_url()

    def test_delete_page_only_accepts_post_requests(self):
        doc, url = self.create_doc()
        res = self.client.get(url)
        self.assertEqual(res.status_code, 405)

    def test_delete_single_revision_is_not_allowed(self):
        """Latest revision cannot be delete if this is the only revision."""
        doc, url = self.create_doc()
        res = self.client.post(url)
        self.assertEqual(res.status_code, 403)

    def test_cannot_delete_revision_in_review(self):
        doc, url = self.create_doc(nb_revisions=5)
        rev = doc.get_latest_revision()
        rev.leader = self.user
        rev.start_review()

        self.assertTrue(rev.is_under_review)

        res = self.client.post(url)
        self.assertEqual(res.status_code, 403)

    def test_delete_latest_revision(self):
        doc, url = self.create_doc(nb_revisions=5)
        doc.refresh_from_db()
        self.assertEqual(doc.get_all_revisions().count(), 5)
        self.assertEqual(doc.current_revision, 5)

        self.client.post(url)
        doc.refresh_from_db()
        self.assertEqual(doc.get_all_revisions().count(), 4)
        self.assertEqual(doc.current_revision, 4)

        self.client.post(url)
        doc.refresh_from_db()
        self.assertEqual(doc.get_all_revisions().count(), 3)
        self.assertEqual(doc.current_revision, 3)

    def test_simple_user_cannot_delete_revision(self):
        doc, delete_url = self.create_doc(nb_revisions=2)
        self.assertEqual(doc.get_all_revisions().count(), 2)
        # User has not delete perms
        user = UserFactory(
            email='testuser@phase.fr',
            password='pass',
            is_superuser=False,
            category=self.category,
        )
        self.client.logout()
        self.client.login(email=user.email, password='pass')

        res = self.client.post(delete_url)

        self.assertEqual(res.status_code, 403)

        doc.refresh_from_db()
        self.assertEqual(doc.get_all_revisions().count(), 2)

    def test_user_with_delete_perms_can_delete_revision(self):
        doc, delete_url = self.create_doc(nb_revisions=2)
        self.assertEqual(doc.get_all_revisions().count(), 2)
        user = UserFactory(
            email='testuser@phase.fr',
            password='pass',
            is_superuser=False,
            category=self.category,
        )
        delete_doc_perm = Permission.objects.get(
            codename='delete_document')
        user.user_permissions.add(delete_doc_perm)
        self.client.logout()
        self.client.login(email=user.email, password='pass')

        self.client.post(delete_url)

        doc.refresh_from_db()
        self.assertEqual(doc.get_all_revisions().count(), 1)


@override_settings(USE_X_SENDFILE=True)
class PrivateDownloadTests(TestCase):
    def setUp(self):
        self.category = CategoryFactory()
        self.user = UserFactory(
            email='test@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category)
        self.client.login(email=self.user.email, password='pass')
        self.doc = DocumentFactory(category=self.category)
        self.rev = self.doc.get_latest_revision()

        pdf_doc = 'sample_doc_pdf.pdf'
        self.sample_pdf = SimpleUploadedFile(pdf_doc, b'content')
        self.url = reverse('revision_file_download', args=[
            self.category.organisation.slug,
            self.category.slug,
            self.doc.document_key,
            self.rev.revision,
            'pdf_file',
        ])

    def test_download_empty_file(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 404)

    def test_download_file(self):
        self.rev.pdf_file = self.sample_pdf
        self.rev.save()

        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_download_file_without_permissions(self):
        self.user.categories.clear()

        self.rev.pdf_file = self.sample_pdf
        self.rev.save()

        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 404)
