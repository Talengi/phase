import os
from os.path import join

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.conf import settings

from accounts.factories import UserFactory
from categories.factories import CategoryFactory
from documents.factories import DocumentFactory
from documents.models import Document
from default_documents.models import DemoMetadataRevision


class DocumentCreateTest(TestCase):

    def setUp(self):
        self.category = CategoryFactory()
        user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category,
        )
        self.create_url = reverse('document_create', args=[
            self.category.organisation.slug,
            self.category.slug,
        ])
        self.client.login(email=user.email, password='pass')
        self.sample_path = join(settings.DJANGO_ROOT, 'documents', 'tests')

    def tearDown(self):
        """Wipe the media root directory after each test."""
        media_root = settings.MEDIA_ROOT
        if os.path.exists(media_root):
            for f in os.listdir(media_root):
                file_path = os.path.join(media_root, f)
                if os.path.isfile(file_path) and file_path.startswith('/tmp/'):
                    os.unlink(file_path)

    def test_creation_errors(self):
        """
        Tests that a document can't be created without required fields.
        """
        required_error = u'This field is required.'
        c = self.client
        r = c.get(self.create_url)
        self.assertEqual(r.status_code, 200)

        r = c.post(self.create_url, {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['form'].errors, {
            'title': [required_error],
        })

    def test_creation_errors_with_files(self):
        """
        Tests that a document can't be created with wrong files.
        """
        extension_error = u'A PDF file is not allowed in this field.'
        c = self.client
        with open(join(self.sample_path, 'sample_doc_native.docx')) as native_file:
            with open(join(self.sample_path, 'sample_doc_pdf.pdf')) as pdf_file:
                r = c.post(self.create_url, {
                    'title': u'a title',
                    'native_file': pdf_file,
                    'pdf_file': native_file,
                })
                self.assertEqual(r.status_code, 200)
                self.assertEqual(r.context['revision_form'].errors, {
                    'native_file': [extension_error],
                })

    def test_creation_success(self):
        """
        Tests that a document can be created with required fields.
        """
        original_number_of_document = Document.objects.all().count()
        c = self.client
        r = c.post(self.create_url, {
            'title': u'a title',
        })
        if r.status_code == 302:
            self.assertEqual(
                original_number_of_document + 1,
                Document.objects.all().count()
            )
        else:
            # Debug purpose
            self.assertEqual(r.context['form'].errors, {})

    def test_creation_sets_document_key(self):
        """
        Tests that a document can be created with required fields.
        """
        c = self.client
        c.post(self.create_url, {
            'title': u'a title',
        }, follow=True)
        doc = Document.objects.all().order_by('-id')[0]
        self.assertEqual(doc.document_key, 'a-title')

        c.post(self.create_url, {
            'title': u'another title',
            'document_key': u'gloubiboulga',
        }, follow=True)
        doc = Document.objects.all().order_by('-id')[0]
        self.assertEqual(doc.document_key, 'gloubiboulga')

    def test_creation_success_with_files(self):
        """
        Tests that a document can be created with files.
        """
        original_number_of_document = Document.objects.all().count()
        c = self.client
        with open(join(self.sample_path, 'sample_doc_native.docx')) as native_file:
            with open(join(self.sample_path, 'sample_doc_pdf.pdf')) as pdf_file:
                r = c.post(self.create_url, {
                    'title': u'a title',
                    'native_file': native_file,
                    'pdf_file': pdf_file,
                })
                if r.status_code == 302:
                    self.assertEqual(
                        original_number_of_document + 1,
                        Document.objects.all().count()
                    )
                else:
                    # Debug purpose
                    self.assertEqual(r.context['form'].errors, {})

    def test_creation_redirect(self):
        """
        Tests that a document creation is redirected to the item
        or another creation form (django-admin like).
        """
        c = self.client
        r = c.post(self.create_url, {
            'title': u'a title',
            'save-create': None,
        }, follow=True)
        self.assertEqual(
            r.redirect_chain,
            [('http://testserver{url}'.format(
                url=self.create_url,
            ), 302)]
        )

        r = c.post(self.create_url, {
            'title': u'another title',
        }, follow=True)
        self.assertEqual(
            r.redirect_chain,
            [('http://testserver{url}'.format(
                url=self.category.get_absolute_url(),
            ), 302)]
        )

    def test_document_related_documents(self):
        c = self.client
        related = [
            DocumentFactory(
                category=self.category,
                document_key='FAC09001-FWF-000-HSE-REP-0004',
                metadata={
                    'title': u'HAZOP related 1',
                },
                revision={
                    'status': 'STD',
                }
            ),
            DocumentFactory(
                category=self.category,
                document_key='FAC09001-FWF-000-HSE-REP-0005',
                metadata={
                    'title': u'HAZOP related 2',
                },
                revision={
                    'status': 'STD',
                }
            )
        ]
        c.post(self.create_url, {
            'document_key': 'FAC09001-FWF-000-HSE-REP-0006',
            'title': u'HAZOP report',
            'related_documents': [doc.pk for doc in related]
        })
        document = Document.objects.get(document_key='FAC09001-FWF-000-HSE-REP-0006')
        metadata = document.metadata
        self.assertEqual(metadata.related_documents.count(), 2)
        self.assertEqual(metadata.related_documents.all()[0].metadata.title, "HAZOP related 1")
        self.assertEqual(metadata.related_documents.all()[1].metadata.title, "HAZOP related 2")


class DocumentEditTest(TestCase):

    def setUp(self):
        user = UserFactory(email='testadmin@phase.fr', password='pass',
                           is_superuser=True)
        self.client.login(email=user.email, password='pass')

    def test_edition_errors(self):
        """
        Tests that a document can't be edited without required fields.
        """
        required_error = u'This field is required.'
        document = Document.objects.create(
            title=u'HAZOP report',
            current_revision_date='2012-04-20',
            sequencial_number="0004",
            discipline="HSE",
            document_type="REP"
        )
        DocumentRevision.objects.create(
            document=document,
            revision=u"00",
            revision_date='2012-04-20',
        )
        c = self.client
        edit_url = reverse(
            "document_edit",
            args=['FAC09001-FWF-000-HSE-REP-0004']
        )
        r = c.get(edit_url)
        self.assertEqual(r.status_code, 200)

        r = c.post(edit_url, {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['form'].errors, {
            'originator': [required_error],
            'discipline': [required_error],
            'title': [required_error],
            'sequencial_number': [required_error],
            'engineering_phase': [required_error],
            'klass': [required_error],
            'document_type': [required_error],
            'contract_number': [required_error],
            'unit': [required_error],
            'current_revision': [required_error],
            'current_revision_date': [required_error],
        })

    def test_edition_success(self):
        """
        Tests that a document can be created with required fields.
        """
        original_number_of_document = Document.objects.all().count()
        document = Document.objects.create(
            title=u'HAZOP report',
            current_revision_date='2012-04-20',
            sequencial_number="0004",
            discipline="HSE",
            document_type="REP"
        )
        DocumentRevision.objects.create(
            document=document,
            revision=u"00",
            revision_date='2012-04-20',
        )
        c = self.client
        edit_url = reverse(
            "document_edit",
            args=['FAC09001-FWF-000-HSE-REP-0004']
        )
        r = c.post(edit_url, {
            'originator': "FWF",
            'discipline': "ARC",
            'title': u'a title',
            'sequencial_number': "0001",
            'engineering_phase': "FEED",
            'klass': 1,
            'document_type': "ANA",
            'contract_number': "FAC09001",
            'unit': "000",
            'current_revision': "00",
            'current_revision_date': "2013-04-20",
        })
        if r.status_code == 302:
            self.assertEqual(
                original_number_of_document + 1,
                Document.objects.all().count()
            )
        else:
            # Debug purpose
            self.assertEqual(r.context['form'].errors, {})

    def test_edition_redirect(self):
        """
        Tests that a document edition is redirected to the item
        or the list.
        """
        document = Document.objects.create(
            title=u'HAZOP report',
            current_revision_date='2012-04-20',
            sequencial_number="0004",
            discipline="HSE",
            document_type="REP"
        )
        DocumentRevision.objects.create(
            document=document,
            revision=u"00",
            revision_date='2012-04-20',
        )
        c = self.client
        edit_url = reverse(
            "document_edit",
            args=['FAC09001-FWF-000-HSE-REP-0004']
        )
        r = c.post(edit_url, {
            'originator': "FWF",
            'discipline': "ARC",
            'title': u'a title',
            'sequencial_number': "0001",
            'engineering_phase': "FEED",
            'klass': 1,
            'document_type': "ANA",
            'contract_number': "FAC09001",
            'unit': "000",
            'current_revision': "01",
            'current_revision_date': "2013-04-20",
        }, follow=True)
        self.assertEqual(
            r.redirect_chain,
            [('http://testserver{url}'.format(
                url=reverse('category_list')
            ), 302)]
        )

        edit_url = reverse(
            "document_edit",
            args=['FAC09001-FWF-000-ARC-ANA-0001']
        )
        r = c.post(edit_url, {
            'originator': "FWF",
            'discipline': "ARC",
            'title': u'a title',
            'sequencial_number': "0001",
            'engineering_phase': "FEED",
            'klass': 1,
            'document_type': "BAS",
            'contract_number': "FAC09001",
            'unit': "000",
            'current_revision': "02",
            'current_revision_date': "2013-04-20",
            'save-view': None,
        }, follow=True)
        self.assertEqual(
            r.redirect_chain,
            [('http://testserver{url}'.format(
                url=reverse(
                    'document_detail',
                    args=['FAC09001-FWF-000-ARC-BAS-0001']
                )
            ), 302)]
        )
