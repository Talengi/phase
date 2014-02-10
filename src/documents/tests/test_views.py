import os
import json

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from accounts.factories import UserFactory, CategoryFactory
from categories.models import Category
from default_documents.factories import MetadataRevisionFactory
from default_documents.models import ContractorDeliverable
from documents.factories import DocumentFactory
from documents.tests.utils import generate_random_documents


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


class DocumentListTest(GenericViewTest):
    fixtures = ['initial_data.json']

    def setUp(self):
        super(DocumentListTest, self).setUp()
        self.url = self.document_list_url
        generate_random_documents(150, self.category)

    def test_document_number(self):
        self.assertGet()
        self.assertContext('documents_active', True)
        self.assertContextLength('object_list', 50)


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


class DocumentFilterTest(TestCase):
    fixtures = ['initial_data', 'initial_documents']

    def setUp(self):
        # Login as admin so we won't be bothered by missing permissions
        category = Category.objects.get(pk=1)
        user = UserFactory(email='testadmin@phase.fr', password='pass',
                           is_superuser=True, category=category)
        self.client.login(email=user.email, password='pass')
        self.filter_url = reverse('document_filter', args=[
            category.organisation.slug,
            category.slug,
        ])

    def test_paging(self):
        """
        Tests the AJAX pagination.
        """
        get_parameters = {
            'length': 10,
            'start': 0,
            'sort_by': 'document_key',
        }
        c = self.client

        # Default: 10 items returned
        r = c.get(self.filter_url, get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['data']), 10)
        self.assertEqual(int(data['total']), 500)
        self.assertEqual(int(data['display']), 10)
        self.assertEqual(
            data['data'],
            [doc.jsonified() for doc in ContractorDeliverable.objects.all()[0:10]]
        )

        # With 100 results
        get_parameters['length'] = 100
        r = c.get(self.filter_url, get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['data']), 100)
        self.assertEqual(int(data['total']), 500)
        self.assertEqual(int(data['display']), 100)
        self.assertEqual(
            data['data'],
            [doc.jsonified() for doc in ContractorDeliverable.objects.all()[0:100]]
        )

        # With 25 results, starting at 10
        get_parameters['length'] = 25
        get_parameters['start'] = 10
        r = c.get(self.filter_url, get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['data']), 25)
        self.assertEqual(int(data['total']), 500)
        self.assertEqual(int(data['display']), 35)
        self.assertEqual(
            data['data'],
            [doc.jsonified() for doc in ContractorDeliverable.objects.all()[10:35]]
        )

    def test_ordering(self):
        """
        Tests the AJAX sorting.
        """
        get_parameters = {
            'length': 10,
            'start': 0,
            'sort_by': 'document_key',
        }
        c = self.client

        # Default: sorted by document_number
        r = c.get(self.filter_url, get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['data']), 10)
        self.assertEqual(
            data['data'],
            [doc.jsonified() for doc in ContractorDeliverable.objects.all()[0:10]]
        )

        # Sorting by title
        get_parameters['sort_by'] = 'title'
        r = c.get(self.filter_url, get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['data']), 10)
        documents = ContractorDeliverable.objects.all()
        self.assertEqual(
            data['data'],
            [doc.jsonified() for doc in documents.order_by('title')[0:10]]
        )

        # Sorting by title (reversed)
        get_parameters['sort_by'] = '-title'
        r = c.get(self.filter_url, get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['data']), 10)
        documents = ContractorDeliverable.objects.all()
        self.assertEqual(
            data['data'],
            [doc.jsonified() for doc in documents.order_by('-title')[0:10]]
        )

    def test_global_filtering(self):
        """
        Tests the AJAX global search.
        """
        get_parameters = {
            'length': 10,
            'start': 0,
            'sort_by': 'document_key',
        }
        c = self.client

        # Searching 'pipeline'
        search_terms = u'pipeline'
        get_parameters['search_terms'] = search_terms
        r = c.get(self.filter_url, get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['data']), 1)

    def test_per_field_filtering(self):
        """
        Tests the AJAX per field search.
        """
        get_parameters = {
            'length': 10,
            'start': 0,
            'sort_by': 'document_key',
        }
        c = self.client

        # Searching 'ASB' status
        status = u'ASB'
        get_parameters['status'] = status
        r = c.get(self.filter_url, get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['data']), 10)
        self.assertEqual(int(data['total']), 44)
        self.assertEqual(int(data['display']), 10)
        documents = ContractorDeliverable.objects.filter(**{
            'latest_revision__status__icontains': status
        })
        self.assertEqual(
            data['data'],
            [doc.jsonified() for doc in documents[0:10]]
        )

        # Searching 'ASB' status + 'PLA' document_type
        status = u'ASB'
        document_type = u'PLA'
        get_parameters['status'] = status
        get_parameters['document_type'] = document_type
        r = c.get(self.filter_url, get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['data']), 1)
        documents = ContractorDeliverable.objects.filter(**{
            'latest_revision__status__icontains': status,
            'document_type__icontains': document_type
        })
        self.assertEqual(
            data['data'],
            [doc.jsonified() for doc in documents[0:10]]
        )

    def test_combining(self):
        """
        Tests the AJAX complex request.
        """
        get_parameters = {
            'length': 10,
            'start': 0,
            'sort_by': 'document_key',
        }
        c = self.client

        # Searching 'pipeline', sorted by title (descending)
        search_terms = u'pipeline'
        get_parameters['search_terms'] = search_terms
        get_parameters['sort_by'] = '-title'
        r = c.get(self.filter_url, get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['data']), 1)

        # Reseting
        get_parameters['search_terms'] = ''
        get_parameters['sort_by'] = 'document_key'

        # Searching 'spec', retrieving 10 items from page 2
        search_terms = u'spec'
        get_parameters['search_terms'] = search_terms
        get_parameters['length'] = 10
        get_parameters['start'] = 10
        r = c.get(self.filter_url, get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['data']), 7)
        self.assertEqual(int(data['display']), 17)

        # Reseting
        get_parameters['search_terms'] = ''
        get_parameters['length'] = 10
        get_parameters['start'] = 0

        # Searching 'spec', retrieving 10 items from page 2, sorted by title
        search_terms = u'spec'
        get_parameters['search_terms'] = search_terms
        get_parameters['length'] = 10
        get_parameters['start'] = 10
        get_parameters['sort_by'] = 'title'
        r = c.get(self.filter_url, get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['data']), 7)
        self.assertEqual(int(data['display']), 17)

        # Reseting
        get_parameters['search_terms'] = ''
        get_parameters['length'] = 10
        get_parameters['start'] = 0
        get_parameters['sort_by'] = 'document_key'

        # Searching 'spec' + status = 'IFR', sorted by title
        search_terms = u'spec'
        status = 'IFR'
        get_parameters['search_terms'] = search_terms
        get_parameters['sort_by'] = '-title'
        get_parameters['status'] = status
        r = c.get(self.filter_url, get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['data']), 4)

    def test_advanced_filtering(self):
        """
        Tests the AJAX advanced search.
        """
        get_parameters = {
            'length': 10,
            'start': 0,
            'sort_by': 'document_key',
        }
        c = self.client

        leader = 2  # user@phase.fr
        get_parameters['leader'] = leader
        r = c.get(self.filter_url, get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['data']), 10)
        self.assertEqual(int(data['total']), 14)
        self.assertEqual(int(data['display']), 10)
        documents = ContractorDeliverable.objects.filter(**{
            'latest_revision__leader': leader
        })
        self.assertEqual(
            data['data'],
            [doc.jsonified() for doc in documents[0:10]]
        )

        leader = 2
        approver = 3  # dc@phase.fr
        get_parameters['leader'] = leader
        get_parameters['approver'] = approver
        r = c.get(self.filter_url, get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['data']), 1)
        documents = ContractorDeliverable.objects.filter(**{
            'latest_revision__leader': leader,
            'latest_revision__approver': approver
        })
        self.assertEqual(
            data['data'],
            [doc.jsonified() for doc in documents[0:10]]
        )


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
        sample_path = 'documents/tests/'
        native_doc = 'sample_doc_native.docx'
        pdf_doc = 'sample_doc_pdf.pdf'

        document = DocumentFactory(
            document_key=u'HAZOP-related',
            category=self.category,
            revision={
                'native_file': SimpleUploadedFile(native_doc, sample_path + native_doc),
                'pdf_file': SimpleUploadedFile(pdf_doc, sample_path + pdf_doc),
            }
        )
        c = self.client
        r = c.get(self.download_url, {
            'document_ids': document.id,
        })
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r._headers, {
            'vary': ('Vary', 'Cookie, Accept-Encoding'),
            'content-length': ('Content-Length', '322'),
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
        r = self.client.get(self.download_url, {'document_ids': [document.id]})
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
        sample_path = 'documents/tests/'
        native_doc = 'sample_doc_native.docx'
        pdf_doc = 'sample_doc_pdf.pdf'

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
        r = self.client.get(self.download_url, {
            'document_ids': [
                document1.id,
                document2.id,
            ],
        })
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r._headers, {
            'vary': ('Vary', 'Cookie, Accept-Encoding'),
            'content-length': ('Content-Length', '630'),
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
        sample_path = 'documents/tests/'
        native_doc = 'sample_doc_native.docx'
        pdf_doc = 'sample_doc_pdf.pdf'

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
        r = c.get(self.download_url, {
            'document_ids': [
                document1.id,
                document2.id,
            ],
            'format': 'pdf',
        })
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r._headers, {
            'vary': ('Vary', 'Cookie, Accept-Encoding'),
            'content-length': ('Content-Length', '320'),
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
        sample_path = 'documents/tests/'
        native_doc = 'sample_doc_native.docx'
        pdf_doc = 'sample_doc_pdf.pdf'

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
        r = self.client.get(document.category.get_download_url(), {
            'document_ids': document.id,
            'revisions': 'all',
        })
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r._headers, {
            'vary': ('Vary', 'Cookie, Accept-Encoding'),
            'content-length': ('Content-Length', '598'),
            'content-type': ('Content-Type', 'application/zip'),
            'content-disposition': (
                'Content-Disposition',
                'attachment; filename=download.zip'
            )
        })
