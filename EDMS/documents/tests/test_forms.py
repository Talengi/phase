from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from documents.models import Document


class DocumentCreateTest(TestCase):
    fixtures = ['initial_data.json']

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
            'revision': [required_error]
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
            'revision': "00"
        })
        if r.status_code == 302:
            self.assertEqual(
                original_number_of_document+1,
                Document.objects.all().count()
            )
        else:
            # Debug purpose
            self.assertEqual(r.context['form'].errors, {})

    def test_creation_redirect(self):
        """
        Tests that a document creation is redirected to the list
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
            'revision': "00",
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
            'document_type': "ANA",
            'contract_number': "FAC09001",
            'unit': "000",
            'revision': "00",
        }, follow=True)
        self.assertEqual(
            r.redirect_chain,
            [('http://testserver{url}'.format(
                url=reverse('document_list')
            ), 302)]
        )
