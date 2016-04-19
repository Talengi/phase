# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from os.path import join

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase

from accounts.factories import UserFactory
from audit_trail.models import Activity
from categories.factories import CategoryFactory
from default_documents.models import DemoMetadataRevision, \
    ContractorDeliverable
from documents.factories import DocumentFactory
from documents.models import Document

from ..forms.filters import filterform_factory


class DocumentCreateTest(TestCase):
    def setUp(self):
        self.category = CategoryFactory()
        self.user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category,
        )
        self.create_url = reverse('document_create', args=[
            self.category.organisation.slug,
            self.category.slug,
        ])
        self.client.login(email=self.user.email, password='pass')
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
        with open(join(self.sample_path,
                       'sample_doc_native.docx')) as native_file:
            with open(
                    join(self.sample_path, 'sample_doc_pdf.pdf')) as pdf_file:
                r = c.post(self.create_url, {
                    'title': u'a title',
                    'native_file': pdf_file,
                    'pdf_file': native_file,
                    'docclass': 1,
                    'created_on': '2015-10-10',
                    'received_date': '2015-10-10',
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

    def test_creation_with_empty_document_key(self):
        """
        Tests that a document can be created with required fields.
        """
        c = self.client
        doc_title = u'a glorious title'
        c.post(self.create_url, {
            'title': doc_title,
            'docclass': 1,
            'created_on': '2015-10-10',
            'received_date': '2015-10-10',
        }, follow=True)
        doc = Document.objects.all().order_by('-id')[0]
        self.assertEqual(doc.document_number, 'a-glorious-title')
        self.assertEqual(doc.document_key, 'a-glorious-title')

        # Check that creation was logged in audit trail
        activity = Activity.objects.latest('created_on')
        self.assertEqual(activity.verb, Activity.VERB_CREATED)
        self.assertEqual(activity.action_object.title, doc_title)
        self.assertEqual(activity.actor, self.user)

    def test_create_with_document_key(self):
        c = self.client
        doc_title = u'another title'
        c.post(self.create_url, {
            'title': doc_title,
            'document_number': u'Gloubi Boulga',
            'docclass': 1,
            'created_on': '2015-10-10',
            'received_date': '2015-10-10',
        }, follow=True)
        doc = Document.objects.all().order_by('-id')[0]
        self.assertEqual(doc.document_number, 'Gloubi Boulga')
        self.assertEqual(doc.document_key, 'GLOUBI-BOULGA')

        # Check audit trail
        activity = Activity.objects.latest('created_on')
        self.assertEqual(activity.verb, Activity.VERB_CREATED)
        self.assertEqual(activity.action_object.title, doc_title)
        self.assertEqual(activity.actor, self.user)

    def test_creation_success_with_files(self):
        """
        Tests that a document can be created with files.
        """
        original_number_of_document = Document.objects.all().count()
        c = self.client
        with open(join(self.sample_path,
                       'sample_doc_native.docx')) as native_file:
            with open(
                    join(self.sample_path, 'sample_doc_pdf.pdf')) as pdf_file:
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
            'docclass': 1,
            'created_on': '2015-10-10',
            'received_date': '2015-10-10',
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
            'docclass': 1,
            'created_on': '2015-10-10',
            'received_date': '2015-10-10',
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
            'document_number': 'FAC09001-FWF-000-HSE-REP-0006',
            'title': u'HAZOP report',
            'docclass': 1,
            'created_on': '2015-10-10',
            'received_date': '2015-10-10',
            'related_documents': [doc.pk for doc in related]
        })
        document = Document.objects.get(
            document_key='FAC09001-FWF-000-HSE-REP-0006')
        metadata = document.metadata
        related = list(metadata.related_documents.all())
        self.assertEqual(len(related), 2)
        related_titles = (related[0].metadata.title, related[1].metadata.title)
        self.assertTrue("HAZOP related 1" in related_titles)
        self.assertTrue("HAZOP related 2" in related_titles)


class DocumentEditTest(TestCase):
    def setUp(self):
        self.category = CategoryFactory()
        self.user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category,
        )
        self.create_url = reverse('document_create', args=[
            self.category.organisation.slug,
            self.category.slug,
        ])
        self.client.login(email=self.user.email, password='pass')
        self.sample_path = join(settings.DJANGO_ROOT, 'documents', 'tests')

    def test_edition_errors(self):
        """
        Tests that a document can't be edited without required fields.
        """
        required_error = u'This field is required.'
        doc = DocumentFactory(
            category=self.category,
            document_key='FAC09001-FWF-000-HSE-REP-0004',
            metadata={
                'title': u'HAZOP related 1',
            },
            revision={
                'status': 'STD',
            }
        )
        c = self.client
        edit_url = doc.get_edit_url()
        r = c.get(edit_url)
        self.assertEqual(r.status_code, 200)

        r = c.post(edit_url, {'document_number': doc.document_key})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['form'].errors, {
            'title': [required_error],
        })

    def test_edition_success(self):
        """
        Tests that a document can be created with required fields.
        """
        original_number_of_document = Document.objects.all().count()
        doc = DocumentFactory(
            category=self.category,
            document_key='FAC09001-FWF-000-HSE-REP-0004',
            metadata={
                'title': u'HAZOP related 1',
            },
            revision={
                'status': 'STD',
            }
        )
        c = self.client
        r = c.post(doc.get_edit_url(), {
            'document_number': doc.document_key,
            'title': u'a new title',
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
        doc = DocumentFactory(
            category=self.category,
            document_key='FAC09001-FWF-000-HSE-REP-0004',
            metadata={
                'title': u'HAZOP related 1',
            },
            revision={
                'status': 'STD',
            }
        )
        c = self.client
        r = c.post(doc.get_edit_url(), {
            'document_number': doc.document_key,
            'title': u'a new title',
            'docclass': 1,
            'created_on': '2015-10-10',
            'received_date': '2015-10-10',
            'save-view': 'View',
        }, follow=True)
        self.assertEqual(
            r.redirect_chain,
            [('http://testserver{url}'.format(
                url=doc.get_absolute_url(),
            ), 302)]
        )

        r = c.post(doc.get_edit_url(), {
            'document_number': doc.document_key,
            'title': u'a new new title',
            'docclass': 1,
            'created_on': '2015-10-10',
            'received_date': '2015-10-10',
        }, follow=True)
        self.assertEqual(
            r.redirect_chain,
            [('http://testserver{url}'.format(
                url=self.category.get_absolute_url(),
            ), 302)]
        )
        # Check that update was logged in audit trail
        activity = Activity.objects.latest('created_on')
        self.assertEqual(activity.verb, Activity.VERB_EDITED)
        self.assertEqual(activity.target.title, u'a new new title')
        self.assertEqual(activity.actor, self.user)

    def test_edition_updates_document_key(self):
        doc = DocumentFactory(
            category=self.category,
            document_key='FAC09001-FWF-000-HSE-REP-0004',
            metadata={
                'title': u'HAZOP related 1',
            },
            revision={
                'status': 'STD',
            }
        )
        c = self.client
        c.post(doc.get_edit_url(), {
            'document_number': 'New Document Number',
            'title': u'a new title',
            'docclass': 1,
            'created_on': '2015-10-10',
            'received_date': '2015-10-10',
            'save-view': 'View',
        }, follow=True)

        doc.refresh_from_db()
        self.assertEqual(doc.document_number, 'New Document Number')
        self.assertEqual(doc.document_key, 'NEW-DOCUMENT-NUMBER')

        metadata = doc.get_metadata()
        self.assertEqual(metadata.document_number, 'New Document Number')
        self.assertEqual(metadata.document_key, 'NEW-DOCUMENT-NUMBER')


class DocumentReviseTest(TestCase):
    def setUp(self):
        self.category = CategoryFactory()
        self.user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category,
        )
        self.client.login(email=self.user.email, password='pass')

    def test_new_revision_form_is_empty(self):
        document = DocumentFactory(
            category=self.category,
            document_key='FAC09001-FWF-000-HSE-REP-0004',
            revision={
                'status': 'STD',
            }
        )
        revision = document.metadata.latest_revision
        self.assertEqual(revision.revision, 1)

        url = reverse('document_revise', args=[
            self.category.organisation.slug,
            self.category.slug,
            document.document_key
        ])
        res = self.client.get(url)
        self.assertNotContains(res, 'selected="selected" value="STD"')

    def test_new_revision_id_is_bumped(self):
        document = DocumentFactory(
            category=self.category,
            document_key='FAC09001-FWF-000-HSE-REP-0004',
            revision={
                'status': 'STD',
            }
        )
        revision = document.metadata.latest_revision
        self.assertEqual(revision.revision, 1)

        url = reverse('document_revise', args=[
            self.category.organisation.slug,
            self.category.slug,
            document.document_key
        ])
        res = self.client.post(url, {
            'document_number': document.document_key,
            'title': document.metadata.title,
            'status': 'SPD',
            'docclass': 1,
            'created_on': '2015-10-10',
            'revision_date': '2015-10-10',
            'received_date': '2015-10-10',
        }, follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'You created revision 02')

        revision = DemoMetadataRevision.objects \
            .filter(metadata__document=document) \
            .order_by('-id')[0]
        self.assertEqual(revision.revision, 2)

        # Check that revision creation was logged in audit trail
        activity = Activity.objects.latest('created_on')
        self.assertEqual(activity.verb, Activity.VERB_CREATED)
        self.assertEqual(activity.action_object, revision)
        self.assertEqual(activity.target, document)
        self.assertEqual(activity.actor, self.user)

    def test_new_revision_files(self):
        """
        Test the on-the-fly renaming when uploading native or pdf files.
        """
        document = DocumentFactory(
            category=self.category,
            document_key='FAC09001-FWF-000-HSE-REP-0004',
            revision={
                'status': 'STD',
            }
        )
        revision = document.metadata.latest_revision
        self.assertEqual(revision.revision, 1)

        url = reverse('document_revise', args=[
            self.category.organisation.slug,
            self.category.slug,
            document.document_key
        ])
        sample_path = join(settings.DJANGO_ROOT, 'documents', 'tests')

        with open(join(sample_path, 'sample_doc_native.docx')) as native_file:
            with open(join(sample_path, 'sample_doc_pdf.pdf')) as pdf_file:
                self.client.post(url, {
                    'document_key': document.document_key,
                    'title': document.metadata.title,
                    'status': 'SPD',
                    'docclass': 1,
                    'created_on': '2015-10-10',
                    'revision_date': '2015-10-10',
                    'received_date': '2015-10-10',
                    'native_file': native_file,
                    'pdf_file': pdf_file,
                }, follow=True)

        revision = DemoMetadataRevision.objects \
            .filter(metadata__document=document) \
            .order_by('-id')[0]
        # Check the right file name creation KEY_REVISION_STATUS[HASH].EXT
        fn_begin = "revisions/{key}_{revision}_{status}".format(
            key=revision.document.document_key,
            revision=revision.name,
            status=revision.status
        )
        # A random hash can be appended to the file name to prevent filename
        # collisions so we check the files beginning and extension
        self.assertTrue(
            revision.native_file.name.startswith(fn_begin)
        )
        self.assertTrue(
            revision.pdf_file.name.startswith(fn_begin)
        )
        self.assertTrue(
            revision.native_file.name.endswith('.docx')
        )
        self.assertTrue(
            revision.pdf_file.name.endswith('.pdf')
        )

    def test_new_revision_can_update_document_key(self):
        doc = DocumentFactory(
            category=self.category,
            document_key='FAC09001-FWF-000-HSE-REP-0004',
            revision={
                'status': 'STD',
            }
        )
        url = reverse('document_revise', args=[
            self.category.organisation.slug,
            self.category.slug,
            doc.document_key
        ])
        self.client.post(url, {
            'document_number': 'Another Document Number',
            'title': doc.metadata.title,
            'status': 'SPD',
            'docclass': 1,
            'created_on': '2015-10-10',
            'revision_date': '2015-10-10',
            'received_date': '2015-10-10',
        }, follow=True)

        doc.refresh_from_db()
        self.assertEqual(doc.document_number, 'Another Document Number')
        self.assertEqual(doc.document_key, 'ANOTHER-DOCUMENT-NUMBER')

        metadata = doc.get_metadata()
        self.assertEqual(metadata.document_number, 'Another Document Number')
        self.assertEqual(metadata.document_key, 'ANOTHER-DOCUMENT-NUMBER')


class FilterFormTest(TestCase):
    def test_filterform_factory(self):
        """Test the filterform_factory behaviour with ordering"""
        # We define a field order. In real life, this should be in PhaseConfig
        fields_order = [
            'approver',
            'docclass',
            'status',
            'unit',
            'discipline',
            'document_type',
            'under_review',
            'overdue',
            'leader']
        doc = ContractorDeliverable

        # Adding this attribute to the model because we do not have any model
        # using this option at the moment
        doc.PhaseConfig.filter_fields_order = fields_order
        form = filterform_factory(doc)()

        # We make alist from field ordered dict keys and get rid of the first
        # fields which are hidden and not defined in filter_fields_order
        # attribute
        form_fields = form.fields.keys()[2:]

        # Checking fields are in the right order
        self.assertEqual(form_fields, fields_order)
