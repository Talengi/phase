from django.db.models import Q
from django.test import TestCase
from django.test.client import Client
from django.utils import simplejson as json
from django.core.urlresolvers import reverse

from documents.models import Document


class DocumentListTest(TestCase):
    fixtures = ['initial_data.json']

    def test_document_number(self):
        """
        Tests that a document list view returns only one document
        to populate table's header.
        """
        c = Client()
        r = c.get(reverse("document_list"))
        self.assertEqual(len(r.context['document_list']), 1)


class DocumenFilterTest(TestCase):
    fixtures = ['initial_data.json']

    def test_paging(self):
        """
        Tests the AJAX pagination.
        """
        get_parameters = {
            'bRegex': False,
            'bRegex_0': False,
            'bRegex_1': False,
            'bRegex_2': False,
            'bRegex_3': False,
            'bRegex_4': False,
            'bRegex_5': False,
            'bRegex_6': False,
            'bRegex_7': False,
            'bRegex_8': False,
            'bSearchable_0': True,
            'bSearchable_1': True,
            'bSearchable_2': True,
            'bSearchable_3': True,
            'bSearchable_4': True,
            'bSearchable_5': True,
            'bSearchable_6': True,
            'bSearchable_7': True,
            'bSearchable_8': True,
            'bSortable_0': True,
            'bSortable_1': True,
            'bSortable_2': True,
            'bSortable_3': True,
            'bSortable_4': True,
            'bSortable_5': True,
            'bSortable_6': True,
            'bSortable_7': True,
            'bSortable_8': True,
            'iColumns': 9,
            'iDisplayLength': 10,
            'iDisplayStart': 0,
            'iSortCol_0': 0,
            'iSortingCols': 1,
            'mDataProp_0': 0,
            'mDataProp_1': 1,
            'mDataProp_2': 2,
            'mDataProp_3': 3,
            'mDataProp_4': 4,
            'mDataProp_5': 5,
            'mDataProp_6': 6,
            'mDataProp_7': 7,
            'mDataProp_8': 8,
            'sColumns': '',
            'sEcho': 111,
            'sSearch': '',
            'sSearch_0': '',
            'sSearch_1': '',
            'sSearch_2': '',
            'sSearch_3': '',
            'sSearch_4': '',
            'sSearch_5': '',
            'sSearch_6': '',
            'sSearch_7': '',
            'sSearch_8': '',
            'sSortDir_0': 'asc',
        }
        c = Client()

        # Default: 10 items returned
        r = c.get(reverse("document_filter"), get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['aaData']), 10)
        self.assertEqual(int(data['sEcho']), 111)
        self.assertEqual(int(data['iTotalRecords']), 500)
        self.assertEqual(int(data['iTotalDisplayRecords']), 500)
        self.assertEqual(
            data['aaData'],
            [doc.jsonified() for doc in Document.objects.all()[0:10]]
        )

        # With 100 results
        get_parameters['iDisplayLength'] = 100
        r = c.get(reverse("document_filter"), get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['aaData']), 100)
        self.assertEqual(int(data['sEcho']), 111)
        self.assertEqual(int(data['iTotalRecords']), 500)
        self.assertEqual(int(data['iTotalDisplayRecords']), 500)
        self.assertEqual(
            data['aaData'],
            [doc.jsonified() for doc in Document.objects.all()[0:100]]
        )

        # With 25 results, starting at 10
        get_parameters['iDisplayLength'] = 25
        get_parameters['iDisplayStart'] = 10
        r = c.get(reverse("document_filter"), get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['aaData']), 25)
        self.assertEqual(int(data['sEcho']), 111)
        self.assertEqual(int(data['iTotalRecords']), 500)
        self.assertEqual(int(data['iTotalDisplayRecords']), 500)
        self.assertEqual(
            data['aaData'],
            [doc.jsonified() for doc in Document.objects.all()[10:35]]
        )

    def test_ordering(self):
        """
        Tests the AJAX sorting.
        """
        get_parameters = {
            'bRegex': False,
            'bRegex_0': False,
            'bRegex_1': False,
            'bRegex_2': False,
            'bRegex_3': False,
            'bRegex_4': False,
            'bRegex_5': False,
            'bRegex_6': False,
            'bRegex_7': False,
            'bRegex_8': False,
            'bSearchable_0': True,
            'bSearchable_1': True,
            'bSearchable_2': True,
            'bSearchable_3': True,
            'bSearchable_4': True,
            'bSearchable_5': True,
            'bSearchable_6': True,
            'bSearchable_7': True,
            'bSearchable_8': True,
            'bSortable_0': True,
            'bSortable_1': True,
            'bSortable_2': True,
            'bSortable_3': True,
            'bSortable_4': True,
            'bSortable_5': True,
            'bSortable_6': True,
            'bSortable_7': True,
            'bSortable_8': True,
            'iColumns': 9,
            'iDisplayLength': 10,
            'iDisplayStart': 0,
            'iSortCol_0': 0,
            'iSortingCols': 1,
            'mDataProp_0': 0,
            'mDataProp_1': 1,
            'mDataProp_2': 2,
            'mDataProp_3': 3,
            'mDataProp_4': 4,
            'mDataProp_5': 5,
            'mDataProp_6': 6,
            'mDataProp_7': 7,
            'mDataProp_8': 8,
            'sColumns': '',
            'sEcho': 111,
            'sSearch': '',
            'sSearch_0': '',
            'sSearch_1': '',
            'sSearch_2': '',
            'sSearch_3': '',
            'sSearch_4': '',
            'sSearch_5': '',
            'sSearch_6': '',
            'sSearch_7': '',
            'sSearch_8': '',
            'sSortDir_0': 'asc',
        }
        c = Client()

        # Default: sorted by document_number
        r = c.get(reverse("document_filter"), get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['aaData']), 10)
        self.assertEqual(
            data['aaData'],
            [doc.jsonified() for doc in Document.objects.all()[0:10]]
        )

        # Sorting by title
        get_parameters['iSortCol_0'] = 1
        r = c.get(reverse("document_filter"), get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['aaData']), 10)
        documents = Document.objects.all()
        self.assertEqual(
            data['aaData'],
            [doc.jsonified() for doc in documents.order_by('title')[0:10]]
        )

        # Sorting by title (reversed)
        get_parameters['iSortCol_0'] = 1
        get_parameters['sSortDir_0'] = 'desc'
        r = c.get(reverse("document_filter"), get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['aaData']), 10)
        documents = Document.objects.all()
        self.assertEqual(
            data['aaData'],
            [doc.jsonified() for doc in documents.order_by('-title')[0:10]]
        )

    def test_filtering(self):
        """
        Tests the AJAX search.
        """
        get_parameters = {
            'bRegex': False,
            'bRegex_0': False,
            'bRegex_1': False,
            'bRegex_2': False,
            'bRegex_3': False,
            'bRegex_4': False,
            'bRegex_5': False,
            'bRegex_6': False,
            'bRegex_7': False,
            'bRegex_8': False,
            'bSearchable_0': True,
            'bSearchable_1': True,
            'bSearchable_2': True,
            'bSearchable_3': True,
            'bSearchable_4': True,
            'bSearchable_5': True,
            'bSearchable_6': True,
            'bSearchable_7': True,
            'bSearchable_8': True,
            'bSortable_0': True,
            'bSortable_1': True,
            'bSortable_2': True,
            'bSortable_3': True,
            'bSortable_4': True,
            'bSortable_5': True,
            'bSortable_6': True,
            'bSortable_7': True,
            'bSortable_8': True,
            'iColumns': 9,
            'iDisplayLength': 10,
            'iDisplayStart': 0,
            'iSortCol_0': 0,
            'iSortingCols': 1,
            'mDataProp_0': 0,
            'mDataProp_1': 1,
            'mDataProp_2': 2,
            'mDataProp_3': 3,
            'mDataProp_4': 4,
            'mDataProp_5': 5,
            'mDataProp_6': 6,
            'mDataProp_7': 7,
            'mDataProp_8': 8,
            'sColumns': '',
            'sEcho': 111,
            'sSearch': '',
            'sSearch_0': '',
            'sSearch_1': '',
            'sSearch_2': '',
            'sSearch_3': '',
            'sSearch_4': '',
            'sSearch_5': '',
            'sSearch_6': '',
            'sSearch_7': '',
            'sSearch_8': '',
            'sSortDir_0': 'asc',
        }
        c = Client()

        # Searching 'pipeline'
        search_terms = u'pipeline'
        get_parameters['sSearch'] = search_terms
        r = c.get(reverse("document_filter"), get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['aaData']), 4)
        self.assertEqual(int(data['iTotalRecords']), 500)
        self.assertEqual(int(data['iTotalDisplayRecords']), 4)
        documents = Document.objects.all()
        q = Q()
        for field in documents[0].searchable_fields():
            q.add(Q(**{'%s__icontains' % field: search_terms}), Q.OR)
        self.assertEqual(
            data['aaData'],
            [doc.jsonified() for doc in documents.filter(q)[0:10]]
        )

    def test_combining(self):
        """
        Tests the AJAX complex request.
        """
        get_parameters = {
            'bRegex': False,
            'bRegex_0': False,
            'bRegex_1': False,
            'bRegex_2': False,
            'bRegex_3': False,
            'bRegex_4': False,
            'bRegex_5': False,
            'bRegex_6': False,
            'bRegex_7': False,
            'bRegex_8': False,
            'bSearchable_0': True,
            'bSearchable_1': True,
            'bSearchable_2': True,
            'bSearchable_3': True,
            'bSearchable_4': True,
            'bSearchable_5': True,
            'bSearchable_6': True,
            'bSearchable_7': True,
            'bSearchable_8': True,
            'bSortable_0': True,
            'bSortable_1': True,
            'bSortable_2': True,
            'bSortable_3': True,
            'bSortable_4': True,
            'bSortable_5': True,
            'bSortable_6': True,
            'bSortable_7': True,
            'bSortable_8': True,
            'iColumns': 9,
            'iDisplayLength': 10,
            'iDisplayStart': 0,
            'iSortCol_0': 0,
            'iSortingCols': 1,
            'mDataProp_0': 0,
            'mDataProp_1': 1,
            'mDataProp_2': 2,
            'mDataProp_3': 3,
            'mDataProp_4': 4,
            'mDataProp_5': 5,
            'mDataProp_6': 6,
            'mDataProp_7': 7,
            'mDataProp_8': 8,
            'sColumns': '',
            'sEcho': 111,
            'sSearch': '',
            'sSearch_0': '',
            'sSearch_1': '',
            'sSearch_2': '',
            'sSearch_3': '',
            'sSearch_4': '',
            'sSearch_5': '',
            'sSearch_6': '',
            'sSearch_7': '',
            'sSearch_8': '',
            'sSortDir_0': 'asc',
        }
        c = Client()

        # Searching 'pipeline', sorted by title (descending)
        search_terms = u'pipeline'
        get_parameters['sSearch'] = search_terms
        get_parameters['iSortCol_0'] = 1
        get_parameters['sSortDir_0'] = 'desc'
        r = c.get(reverse("document_filter"), get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['aaData']), 4)
        self.assertEqual(int(data['iTotalRecords']), 500)
        self.assertEqual(int(data['iTotalDisplayRecords']), 4)
        documents = Document.objects.all()
        q = Q()
        for field in documents[0].searchable_fields():
            q.add(Q(**{'%s__icontains' % field: search_terms}), Q.OR)
        documents = documents.filter(q).order_by('-title')
        self.assertEqual(
            data['aaData'],
            [doc.jsonified() for doc in documents[0:10]]
        )
        # Reseting
        get_parameters['sSearch'] = ''
        get_parameters['iSortCol_0'] = 0
        get_parameters['sSortDir_0'] = 'asc'

        # Searching 'spec', retrieving 10 items from page 2
        search_terms = u'spec'
        get_parameters['sSearch'] = search_terms
        get_parameters['iDisplayLength'] = 10
        get_parameters['iDisplayStart'] = 10
        r = c.get(reverse("document_filter"), get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['aaData']), 8)
        self.assertEqual(int(data['iTotalRecords']), 500)
        self.assertEqual(int(data['iTotalDisplayRecords']), 18)
        documents = Document.objects.all()
        q = Q()
        for field in documents[0].searchable_fields():
            q.add(Q(**{'%s__icontains' % field: search_terms}), Q.OR)
        documents = documents.filter(q)
        self.assertEqual(
            data['aaData'],
            [doc.jsonified() for doc in documents[10:20]]
        )
        # Reseting
        get_parameters['sSearch'] = ''
        get_parameters['iDisplayLength'] = 0
        get_parameters['iDisplayStart'] = 'asc'

        # Searching 'spec', retrieving 10 items from page 2, sorted by title
        search_terms = u'spec'
        get_parameters['sSearch'] = search_terms
        get_parameters['iDisplayLength'] = 10
        get_parameters['iDisplayStart'] = 10
        get_parameters['iSortCol_0'] = 1
        r = c.get(reverse("document_filter"), get_parameters)
        data = json.loads(r.content)
        self.assertEqual(len(data['aaData']), 8)
        self.assertEqual(int(data['iTotalRecords']), 500)
        self.assertEqual(int(data['iTotalDisplayRecords']), 18)
        documents = Document.objects.all()
        q = Q()
        for field in documents[0].searchable_fields():
            q.add(Q(**{'%s__icontains' % field: search_terms}), Q.OR)
        documents = documents.filter(q).order_by('title')
        self.assertEqual(
            data['aaData'],
            [doc.jsonified() for doc in documents[10:20]]
        )
