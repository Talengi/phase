import os

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from documents.models import Document, DocumentRevision


class DocumentCreateTest(TestCase):

    def test_creation_errors(self):
        """
        Tests that a document can't be created without required fields.
        """
        required_error = u'This field is required.'
        c = Client()
        r = c.get(reverse("document_create"))
        self.assertEqual(r.status_code, 200)

        r = c.post(reverse("document_create"), {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['form'].errors, {
            'originator': [required_error],
            'discipline': [required_error],
            'title': [required_error],
            'sequencial_number': [required_error],
            'engeenering_phase': [required_error],
            'klass': [required_error],
            'document_type': [required_error],
            'contract_number': [required_error],
            'unit': [required_error],
            'current_revision': [required_error],
            'current_revision_date': [required_error],
        })

    def test_creation_errors_with_files(self):
        """
        Tests that a document can't be created with wrong files.
        """
        extension_error = u'A PDF file is not allowed in this field.'
        sample_path = 'EDMS/documents/tests/'
        c = Client()
        with open(sample_path+'sample_doc_native.docx') as native_file:
            with open(sample_path+'sample_doc_pdf.pdf') as pdf_file:
                r = c.post(reverse("document_create"), {
                    'originator': "FWF",
                    'discipline': "ARC",
                    'title': u'a title',
                    'sequencial_number': "0001",
                    'engeenering_phase': "FEED",
                    'klass': 1,
                    'document_type': "ANA",
                    'contract_number': "FAC09001",
                    'unit': "000",
                    'current_revision': "00",
                    'current_revision_date': "2013-04-20",
                    'native_file': pdf_file,
                    'pdf_file': native_file,
                })
                self.assertEqual(r.status_code, 200)
                self.assertEqual(r.context['form'].errors, {
                    'native_file': [extension_error],
                })

    def test_creation_success(self):
        """
        Tests that a document can be created with required fields.
        """
        original_number_of_document = Document.objects.all().count()
        c = Client()
        r = c.post(reverse("document_create"), {
            'originator': "FWF",
            'discipline': "ARC",
            'title': u'a title',
            'sequencial_number': "0001",
            'engeenering_phase': "FEED",
            'klass': 1,
            'document_type': "ANA",
            'contract_number': "FAC09001",
            'unit': "000",
            'current_revision': "00",
            'current_revision_date': "2013-04-20",
        })
        if r.status_code == 302:
            self.assertEqual(
                original_number_of_document+1,
                Document.objects.all().count()
            )
        else:
            # Debug purpose
            self.assertEqual(r.context['form'].errors, {})

    def test_creation_success_with_files(self):
        """
        Tests that a document can be created with files.
        """
        original_number_of_document = Document.objects.all().count()
        sample_path = 'EDMS/documents/tests/'
        c = Client()
        with open(sample_path+'sample_doc_native.docx') as native_file:
            with open(sample_path+'sample_doc_pdf.pdf') as pdf_file:
                r = c.post(reverse("document_create"), {
                    'originator': "FWF",
                    'discipline': "ARC",
                    'title': u'a title',
                    'sequencial_number': "0001",
                    'engeenering_phase': "FEED",
                    'klass': 1,
                    'document_type': "ANA",
                    'contract_number': "FAC09001",
                    'unit': "000",
                    'current_revision': "00",
                    'current_revision_date': "2013-04-20",
                    'native_file': native_file,
                    'pdf_file': pdf_file,
                })
                if r.status_code == 302:
                    self.assertEqual(
                        original_number_of_document+1,
                        Document.objects.all().count()
                    )
                    # Delete created files
                    media_path = 'EDMS/media/'
                    file_name = 'FAC09001-FWF-000-ARC-ANA-0001_00'
                    os.remove(media_path+file_name+'.docx')
                    os.remove(media_path+file_name+'.pdf')
                else:
                    # Debug purpose
                    self.assertEqual(r.context['form'].errors, {})

    def test_creation_redirect(self):
        """
        Tests that a document creation is redirected to the item
        or another creation form (django-admin like).
        """
        c = Client()
        r = c.post(reverse("document_create"), {
            'originator': "FWF",
            'discipline': "ARC",
            'title': u'a title',
            'sequencial_number': "0001",
            'engeenering_phase': "FEED",
            'klass': 1,
            'document_type': "ANA",
            'contract_number': "FAC09001",
            'unit': "000",
            'current_revision': "00",
            'current_revision_date': "2013-04-20",
            'save-create': None,
        }, follow=True)
        self.assertEqual(
            r.redirect_chain,
            [('http://testserver{url}'.format(
                url=reverse('document_create')
            ), 302)]
        )

        r = c.post(reverse("document_create"), {
            'originator': "FWF",
            'discipline': "ARC",
            'title': u'a title',
            'sequencial_number': "0001",
            'engeenering_phase': "FEED",
            'klass': 1,
            'document_type': "BAS",
            'contract_number': "FAC09001",
            'unit': "000",
            'current_revision': "00",
            'current_revision_date': "2013-04-20",
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


class DocumentEditTest(TestCase):

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
        c = Client()
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
            'engeenering_phase': [required_error],
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
        c = Client()
        edit_url = reverse(
            "document_edit",
            args=['FAC09001-FWF-000-HSE-REP-0004']
        )
        r = c.post(edit_url, {
            'originator': "FWF",
            'discipline': "ARC",
            'title': u'a title',
            'sequencial_number': "0001",
            'engeenering_phase': "FEED",
            'klass': 1,
            'document_type': "ANA",
            'contract_number': "FAC09001",
            'unit': "000",
            'current_revision': "00",
            'current_revision_date': "2013-04-20",
        })
        if r.status_code == 302:
            self.assertEqual(
                original_number_of_document+1,
                Document.objects.all().count()
            )
        else:
            # Debug purpose
            self.assertEqual(r.context['form'].errors, {})

    def test_edition_redirect(self):
        """
        Tests that a document edition is redirected to the item
        or another creation form (django-admin like).
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
        c = Client()
        edit_url = reverse(
            "document_edit",
            args=['FAC09001-FWF-000-HSE-REP-0004']
        )
        r = c.post(edit_url, {
            'originator': "FWF",
            'discipline': "ARC",
            'title': u'a title',
            'sequencial_number': "0001",
            'engeenering_phase': "FEED",
            'klass': 1,
            'document_type': "ANA",
            'contract_number': "FAC09001",
            'unit': "000",
            'current_revision': "01",
            'current_revision_date': "2013-04-20",
            'save-create': None,
        }, follow=True)
        self.assertEqual(
            r.redirect_chain,
            [('http://testserver{url}'.format(
                url=reverse('document_create')
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
            'engeenering_phase': "FEED",
            'klass': 1,
            'document_type': "BAS",
            'contract_number': "FAC09001",
            'unit': "000",
            'current_revision': "02",
            'current_revision_date': "2013-04-20",
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
