import os

from django.db.models import Q
from django.contrib import auth
from django.test import TestCase
from django.test.client import Client
from django.utils import simplejson as json
from django.core.urlresolvers import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from documents.models import Document, DocumentRevision, Favorite

User = auth.get_user_model()


class GenericViewTest(TestCase):

    def setUp(self):
        self.client = Client()

    def assertGet(self, num_queries, parameters={}, auth=None, status_code=200):
        if auth:
            response = self.client.login(**auth)
            self.assertEqual(response, True)
        with self.assertNumQueries(num_queries):
            response = self.client.get(self.url, parameters, follow=True)
        self.assertEqual(response.status_code, status_code)
        self.content = response.content
        self.context = response.context

    def assertPost(self, num_queries, parameters={}, auth=None, status_code=200):
        if auth:
            response = self.client.login(**auth)
            self.assertEqual(response, True)
        with self.assertNumQueries(num_queries):
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
    url = reverse("document_list")

    def test_document_number(self):
        self.assertGet(3)
        self.assertContext('documents_active', True)
        self.assertContextLength('document_list', 50)


class DocumentDetailTest(GenericViewTest):

    def test_document_number(self):
        """
        Tests that a document detail returns a document and his form.
        """
        document = Document.objects.create(
            title=u'HAZOP report',
            current_revision_date='2012-04-20',
            sequencial_number="0004",
            discipline="HSE",
            document_type="REP",
            current_revision=u"03",
        )
        DocumentRevision.objects.create(
            document=document,
            revision=u"03",
            revision_date='2012-04-20',
        )
        self.url = reverse("document_detail", args=[document.document_number])
        self.assertGet(6)
        self.assertContext('document', document)
        self.assertEqual(
            self.context['document'].document_number,
            u'FAC09001-FWF-000-HSE-REP-0004'
        )
        self.assertEqual(len(self.context['form'].fields.keys()), 49)

    def test_document_related_documents(self):
        documents = [
            Document.objects.create(
                title=u'HAZOP related 1',
                current_revision_date='2012-04-20',
                sequencial_number="0004",
                discipline="HSE",
                document_type="REP",
                current_revision=u"03",
            ),
            Document.objects.create(
                title=u'HAZOP related 2',
                current_revision_date='2012-04-20',
                sequencial_number="0005",
                discipline="HSE",
                document_type="REP",
                current_revision=u"03",
            )
        ]
        document = Document.objects.create(
            title=u'HAZOP report',
            current_revision_date='2012-04-20',
            sequencial_number="0006",
            discipline="HSE",
            document_type="REP",
            current_revision=u"03",
        )
        document.related_documents = documents
        self.url = reverse("document_detail", args=[document.document_number])
        self.assertGet(7)
        self.assertRendering(
            '<li><a href="/detail/{0}/">{0} - HAZOP related 1</a></li>'
            .format(documents[0].document_number)
        )
        self.assertRendering(
            '<li><a href="/detail/{0}/">{0} - HAZOP related 2</a></li>'
            .format(documents[1].document_number)
        )


class DocumenFilterTest(TestCase):
    fixtures = ['initial_data.json']

    def test_paging(self):
        """
        Tests the AJAX pagination.
        """
        get_parameters = {
            'length': 10,
            'start': 0,
            'sort_by': 'document_number',
        }
        c = Client()

        # Default: 10 items returned
        r = c.get(reverse("document_filter"), get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['data']), 10)
        self.assertEqual(int(data['total']), 500)
        self.assertEqual(int(data['display']), 10)
        self.assertEqual(
            data['data'],
            [doc.jsonified() for doc in Document.objects.all()[0:10]]
        )

        # With 100 results
        get_parameters['length'] = 100
        r = c.get(reverse("document_filter"), get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['data']), 100)
        self.assertEqual(int(data['total']), 500)
        self.assertEqual(int(data['display']), 100)
        self.assertEqual(
            data['data'],
            [doc.jsonified() for doc in Document.objects.all()[0:100]]
        )

        # With 25 results, starting at 10
        get_parameters['length'] = 25
        get_parameters['start'] = 10
        r = c.get(reverse("document_filter"), get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['data']), 25)
        self.assertEqual(int(data['total']), 500)
        self.assertEqual(int(data['display']), 35)
        self.assertEqual(
            data['data'],
            [doc.jsonified() for doc in Document.objects.all()[10:35]]
        )

    def test_ordering(self):
        """
        Tests the AJAX sorting.
        """
        get_parameters = {
            'length': 10,
            'start': 0,
            'sort_by': 'document_number',
        }
        c = Client()

        # Default: sorted by document_number
        r = c.get(reverse("document_filter"), get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['data']), 10)
        self.assertEqual(
            data['data'],
            [doc.jsonified() for doc in Document.objects.all()[0:10]]
        )

        # Sorting by title
        get_parameters['sort_by'] = 'title'
        r = c.get(reverse("document_filter"), get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['data']), 10)
        documents = Document.objects.all()
        self.assertEqual(
            data['data'],
            [doc.jsonified() for doc in documents.order_by('title')[0:10]]
        )

        # Sorting by title (reversed)
        get_parameters['sort_by'] = '-title'
        r = c.get(reverse("document_filter"), get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['data']), 10)
        documents = Document.objects.all()
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
            'sort_by': 'document_number',
        }
        c = Client()

        # Searching 'pipeline'
        search_terms = u'pipeline'
        get_parameters['search_terms'] = search_terms
        r = c.get(reverse("document_filter"), get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['data']), 1)
        documents = Document.objects.all()
        q = Q()
        for field in documents[0].searchable_fields():
            q.add(Q(**{'%s__icontains' % field: search_terms}), Q.OR)
        self.assertEqual(
            data['data'],
            [doc.jsonified() for doc in documents.filter(q)[0:10]]
        )

    def test_per_field_filtering(self):
        """
        Tests the AJAX per field search.
        """
        get_parameters = {
            'length': 10,
            'start': 0,
            'sort_by': 'document_number',
        }
        c = Client()

        # Searching 'ASB' status
        status = u'ASB'
        get_parameters['status'] = status
        r = c.get(reverse("document_filter"), get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['data']), 10)
        self.assertEqual(int(data['total']), 44)
        self.assertEqual(int(data['display']), 10)
        documents = Document.objects.all()
        documents = documents.filter(**{
            'status__icontains': status
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
        r = c.get(reverse("document_filter"), get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['data']), 1)
        documents = Document.objects.all()
        documents = documents.filter(**{
            'status__icontains': status,
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
            'sort_by': 'document_number',
        }
        c = Client()

        # Searching 'pipeline', sorted by title (descending)
        search_terms = u'pipeline'
        get_parameters['search_terms'] = search_terms
        get_parameters['sort_by'] = '-title'
        r = c.get(reverse("document_filter"), get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['data']), 1)
        documents = Document.objects.all()
        q = Q()
        for field in documents[0].searchable_fields():
            q.add(Q(**{'%s__icontains' % field: search_terms}), Q.OR)
        documents = documents.filter(q).order_by('-title')
        self.assertEqual(
            data['data'],
            [doc.jsonified() for doc in documents[0:10]]
        )
        # Reseting
        get_parameters['search_terms'] = ''
        get_parameters['sort_by'] = 'document_number'

        # Searching 'spec', retrieving 10 items from page 2
        search_terms = u'spec'
        get_parameters['search_terms'] = search_terms
        get_parameters['length'] = 10
        get_parameters['start'] = 10
        r = c.get(reverse("document_filter"), get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['data']), 7)
        self.assertEqual(int(data['display']), 17)
        documents = Document.objects.all()
        q = Q()
        for field in documents[0].searchable_fields():
            q.add(Q(**{'%s__icontains' % field: search_terms}), Q.OR)
        documents = documents.filter(q)
        self.assertEqual(
            data['data'],
            [doc.jsonified() for doc in documents[10:20]]
        )
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
        r = c.get(reverse("document_filter"), get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['data']), 7)
        self.assertEqual(int(data['display']), 17)
        documents = Document.objects.all()
        q = Q()
        for field in documents[0].searchable_fields():
            q.add(Q(**{'%s__icontains' % field: search_terms}), Q.OR)
        documents = documents.filter(q).order_by('title')
        self.assertEqual(
            data['data'],
            [doc.jsonified() for doc in documents[10:20]]
        )
        # Reseting
        get_parameters['search_terms'] = ''
        get_parameters['length'] = 10
        get_parameters['start'] = 0
        get_parameters['sort_by'] = 'document_number'

        # Searching 'spec' + status = 'IFR', sorted by title
        search_terms = u'spec'
        status = u'IFR'
        get_parameters['search_terms'] = search_terms
        get_parameters['sort_by'] = '-title'
        get_parameters['status'] = status
        r = c.get(reverse("document_filter"), get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['data']), 4)
        documents = Document.objects.all()
        q = Q()
        for field in documents[0].searchable_fields():
            q.add(Q(**{'%s__icontains' % field: search_terms}), Q.OR)
        documents = documents.filter(q)
        documents = documents.filter(**{
            'status__icontains': status,
        })
        self.assertEqual(
            data['data'],
            [doc.jsonified() for doc in documents.order_by('-title')[0:10]]
        )

    def test_advanced_filtering(self):
        """
        Tests the AJAX advanced search.
        """
        get_parameters = {
            'length': 10,
            'start': 0,
            'sort_by': 'document_number',
        }
        c = Client()

        # Searching 'Matthieu Lamy' as a leader
        leader = 5
        get_parameters['leader'] = leader
        r = c.get(reverse("document_filter"), get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['data']), 10)
        self.assertEqual(int(data['total']), 33)
        self.assertEqual(int(data['display']), 10)
        documents = Document.objects.all()
        documents = documents.filter(**{
            'leader': leader
        })
        self.assertEqual(
            data['data'],
            [doc.jsonified() for doc in documents[0:10]]
        )

        # Searching 'Matthieu Lamy' as a leader
        # + 'Pierre-Yves Boucher' as an approver
        leader = 5
        approver = 1
        get_parameters['leader'] = leader
        get_parameters['approver'] = approver
        r = c.get(reverse("document_filter"), get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['data']), 4)
        documents = Document.objects.all()
        documents = documents.filter(**{
            'leader': leader,
            'approver': approver
        })
        self.assertEqual(
            data['data'],
            [doc.jsonified() for doc in documents[0:10]]
        )


class DocumentDownloadTest(TestCase):

    def test_unique_document_download(self):
        """
        Tests that a document download returns a zip file of the latest revision.
        """
        document = Document.objects.create(
            title=u'HAZOP report',
            current_revision_date='2012-04-20',
            sequencial_number="0004",
            discipline="HSE",
            document_type="REP",
            current_revision=u"00",
        )
        sample_path = 'documents/tests/'
        native_doc = 'sample_doc_native.docx'
        pdf_doc = 'sample_doc_pdf.pdf'

        DocumentRevision.objects.create(
            document=document,
            revision=u"00",
            revision_date='2012-04-20',
            native_file=SimpleUploadedFile(native_doc, sample_path+native_doc),
            pdf_file=SimpleUploadedFile(pdf_doc, sample_path+pdf_doc),
        )
        c = Client()
        r = c.get(reverse("document_download"), {
            'document_ids': document.id,
        })
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r._headers, {
            'vary': ('Vary', 'Accept-Encoding'),
            'content-length': ('Content-Length', '398'),
            'content-type': ('Content-Type', 'application/zip'),
            'content-disposition': (
                'Content-Disposition',
                'attachment; filename=download.zip'
            )
        })
        media_path = 'EDMS/media/'
        file_name = 'FAC09001-FWF-000-HSE-REP-0004_00'
        os.remove(media_path+file_name+'.docx')
        os.remove(media_path+file_name+'.pdf')

    def test_empty_document_download(self):
        """
        Tests that a document download returns an empty zip file.
        """
        document = Document.objects.create(
            title=u'HAZOP report',
            current_revision_date='2012-04-20',
            sequencial_number="0004",
            discipline="HSE",
            document_type="REP",
            current_revision=u"00",
        )

        DocumentRevision.objects.create(
            document=document,
            revision=u"00",
            revision_date='2012-04-20',
        )
        c = Client()
        r = c.get(reverse("document_download"), {
            'document_ids': document.id,
        })
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r._headers, {
            'content-length': ('Content-Length', '22'),
            'content-type': ('Content-Type', 'application/zip'),
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
        document1 = Document.objects.create(
            title=u'HAZOP report',
            current_revision_date='2012-04-20',
            sequencial_number="0004",
            discipline="HSE",
            document_type="REP",
            current_revision=u"00",
        )
        sample_path = 'documents/tests/'
        native_doc = 'sample_doc_native.docx'
        pdf_doc = 'sample_doc_pdf.pdf'

        DocumentRevision.objects.create(
            document=document1,
            revision=u"00",
            revision_date='2012-04-20',
            native_file=SimpleUploadedFile(native_doc, sample_path+native_doc),
            pdf_file=SimpleUploadedFile(pdf_doc, sample_path+pdf_doc),
        )
        document2 = Document.objects.create(
            title=u'HAZOP report',
            current_revision_date='2012-04-20',
            sequencial_number="0004",
            discipline="ARC",
            document_type="REP",
            current_revision=u"00",
        )
        sample_path = 'documents/tests/'
        native_doc = 'sample_doc_native.docx'
        pdf_doc = 'sample_doc_pdf.pdf'

        DocumentRevision.objects.create(
            document=document2,
            revision=u"00",
            revision_date='2012-04-20',
            native_file=SimpleUploadedFile(native_doc, sample_path+native_doc),
            pdf_file=SimpleUploadedFile(pdf_doc, sample_path+pdf_doc),
        )
        c = Client()
        r = c.get(reverse("document_download"), {
            'document_ids': [
                document1.id,
                document2.id,
            ],
        })
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r._headers, {
            'vary': ('Vary', 'Accept-Encoding'),
            'content-length': ('Content-Length', '758'),
            'content-type': ('Content-Type', 'application/zip'),
            'content-disposition': (
                'Content-Disposition',
                'attachment; filename=download.zip'
            )
        })
        media_path = 'EDMS/media/'
        file_name = 'FAC09001-FWF-000-HSE-REP-0004_00'
        os.remove(media_path+file_name+'.docx')
        os.remove(media_path+file_name+'.pdf')
        file_name = 'FAC09001-FWF-000-ARC-REP-0004_00'
        os.remove(media_path+file_name+'.docx')
        os.remove(media_path+file_name+'.pdf')

    def test_multiple_pdf_document_download(self):
        """
        Tests that download returns a zip file of the latest revision
        of pdf documents.
        """
        document1 = Document.objects.create(
            title=u'HAZOP report',
            current_revision_date='2012-04-20',
            sequencial_number="0004",
            discipline="HSE",
            document_type="REP",
            current_revision=u"00",
        )
        sample_path = 'documents/tests/'
        native_doc = 'sample_doc_native.docx'
        pdf_doc = 'sample_doc_pdf.pdf'

        DocumentRevision.objects.create(
            document=document1,
            revision=u"00",
            revision_date='2012-04-20',
            native_file=SimpleUploadedFile(native_doc, sample_path+native_doc),
            pdf_file=SimpleUploadedFile(pdf_doc, sample_path+pdf_doc),
        )
        document2 = Document.objects.create(
            title=u'HAZOP report',
            current_revision_date='2012-04-20',
            sequencial_number="0004",
            discipline="ARC",
            document_type="REP",
            current_revision=u"00",
        )
        sample_path = 'documents/tests/'
        native_doc = 'sample_doc_native.docx'
        pdf_doc = 'sample_doc_pdf.pdf'

        DocumentRevision.objects.create(
            document=document2,
            revision=u"00",
            revision_date='2012-04-20',
            native_file=SimpleUploadedFile(native_doc, sample_path+native_doc),
            pdf_file=SimpleUploadedFile(pdf_doc, sample_path+pdf_doc),
        )
        c = Client()
        r = c.get(reverse("document_download"), {
            'document_ids': [
                document1.id,
                document2.id,
            ],
            'format': 'pdf',
        })
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r._headers, {
            'vary': ('Vary', 'Accept-Encoding'),
            'content-length': ('Content-Length', '384'),
            'content-type': ('Content-Type', 'application/zip'),
            'content-disposition': (
                'Content-Disposition',
                'attachment; filename=download.zip'
            )
        })
        media_path = 'EDMS/media/'
        file_name = 'FAC09001-FWF-000-HSE-REP-0004_00'
        os.remove(media_path+file_name+'.docx')
        os.remove(media_path+file_name+'.pdf')
        file_name = 'FAC09001-FWF-000-ARC-REP-0004_00'
        os.remove(media_path+file_name+'.docx')
        os.remove(media_path+file_name+'.pdf')

    def test_all_revisions_document_download(self):
        """
        Tests that download returns a zip file of all revisions
        of a document.
        """
        document = Document.objects.create(
            title=u'HAZOP report',
            current_revision_date='2012-04-20',
            sequencial_number="0004",
            discipline="HSE",
            document_type="REP",
            current_revision=u"00",
        )
        sample_path = 'documents/tests/'
        native_doc = 'sample_doc_native.docx'
        pdf_doc = 'sample_doc_pdf.pdf'

        DocumentRevision.objects.create(
            document=document,
            revision=u"00",
            revision_date='2012-04-20',
            native_file=SimpleUploadedFile(native_doc, sample_path+native_doc),
            pdf_file=SimpleUploadedFile(pdf_doc, sample_path+pdf_doc),
        )
        DocumentRevision.objects.create(
            document=document,
            revision=u"01",
            revision_date='2012-04-21',
            native_file=SimpleUploadedFile(native_doc, sample_path+native_doc),
            pdf_file=SimpleUploadedFile(pdf_doc, sample_path+pdf_doc),
        )
        c = Client()
        r = c.get(reverse("document_download"), {
            'document_ids': document.id,
            'revisions': 'all',
        })
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r._headers, {
            'vary': ('Vary', 'Accept-Encoding'),
            'content-length': ('Content-Length', '758'),
            'content-type': ('Content-Type', 'application/zip'),
            'content-disposition': (
                'Content-Disposition',
                'attachment; filename=download.zip'
            )
        })
        media_path = 'EDMS/media/'
        file_name = 'FAC09001-FWF-000-HSE-REP-0004_00'
        os.remove(media_path+file_name+'.docx')
        os.remove(media_path+file_name+'.pdf')
        file_name = 'FAC09001-FWF-000-HSE-REP-0004_01'
        os.remove(media_path+file_name+'.docx')
        os.remove(media_path+file_name+'.pdf')


class FavoriteTest(GenericViewTest):
    url = reverse("favorite_list")

    def test_favorite_list(self):
        """
        Tests that a favorite list is accessible if logged in.
        """
        User.objects.create_user(
            'david',
            'foo@bar.fr',
            'password',
        )

        # Anonymous user
        self.assertRedirect(
            'http://testserver{url}?next=/favorites/'.format(
                url=reverse('document_list'))
        )

        # Logged in user
        auth = {'username': 'david', 'password': 'password'}
        self.assertGet(4, auth=auth)
        self.assertRendering('<p>You do not have any favorite document.</p>')

    def test_favorite_privacy(self):
        """
        Tests that a favorite is not shared accross users.
        """
        david = User.objects.create_user(
            'david',
            'foo@bar.fr',
            'password',
        )
        User.objects.create_user(
            'matthieu',
            'foo@bar.fr',
            'password',
        )
        document = Document.objects.create(
            title=u'HAZOP report',
            current_revision_date='2012-04-20',
            sequencial_number="0004",
            discipline="HSE",
            document_type="REP",
            current_revision=u"03",
        )
        favorite = Favorite.objects.create(
            document=document,
            user=david
        )

        # Right user
        auth = {'username': 'david', 'password': 'password'}
        self.assertGet(5, auth=auth)
        self.assertRendering('<td>%s</td>' % favorite.document.title)

        # Wrong user
        auth = {'username': 'matthieu', 'password': 'password'}
        self.assertGet(4, auth=auth)
        self.assertRendering('<p>You do not have any favorite document.</p>')

    def test_favorite_creation(self):
        """
        Tests that a favorite creation is possible.
        """
        user = User.objects.create_user(
            'david',
            'foo@bar.fr',
            'password',
        )
        document = Document.objects.create(
            title=u'HAZOP report',
            current_revision_date='2012-04-20',
            sequencial_number="0004",
            discipline="HSE",
            document_type="REP",
            current_revision=u"03",
        )
        self.url = reverse("favorite_create")
        self.assertPost(5, {
            'document': document.id,
            'user': user.id,
        })
        # First favorite created
        self.assertEqual(self.content, '1')
        self.assertEqual(Favorite.objects.all().count(), 1)

    def test_favorite_deletion(self):
        """
        Tests that a favorite deletion is possible.
        """
        user = User.objects.create_user(
            'david',
            'foo@bar.fr',
            'password',
        )
        document = Document.objects.create(
            title=u'HAZOP report',
            current_revision_date='2012-04-20',
            sequencial_number="0004",
            discipline="HSE",
            document_type="REP",
            current_revision=u"03",
        )
        favorite = Favorite.objects.create(
            document=document,
            user=user
        )
        self.url = reverse("favorite_delete", args=[favorite.pk])
        self.assertPost(2, status_code=302)
        self.assertEqual(Favorite.objects.all().count(), 0)
