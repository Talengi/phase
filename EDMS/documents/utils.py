import zipfile
import tempfile
try:
    import zlib
    compression = zipfile.ZIP_DEFLATED
except:
    compression = zipfile.ZIP_STORED

from django.db.models import Q

from documents.models import Document


def filter_documents(queryset, data):
    """Filter documents from a queryset given data from DataTables.

    Documentation (lack of is more accurate though):
    http://www.datatables.net/examples/server_side/server_side.html
    """
    # Dummy document to retrieve displayed fields
    # TODO: find a better way to achieve this
    document = Document.objects.latest('document_number')
    display_fields = document.display_fields()
    searchable_fields = document.searchable_fields()

    # Paging (done at the view level, the whole queryset is still required)

    # Ordering
    sort_column = data.get('sort_column', None)
    if sort_column:
        sort_direction = data['sort_direction'] == u'desc' and u'-' or u''
        if sort_column == 0:  # fallback on document_number
            column_name = (sort_direction+'document_number',)
        else:
            column_name = (sort_direction+display_fields[sort_column][1],)
        queryset = queryset.order_by(*column_name)

    # Filtering (global)
    search_terms = data.get('search_terms', None)
    if search_terms:
        q = Q()
        for field in searchable_fields:
            q.add(Q(**{'%s__icontains' % field: search_terms}), Q.OR)
        queryset = queryset.filter(q)

    # Filtering (advanced)
    advanced_args = {}
    parameter_names = (
        'status', 'revision', 'unit', 'discipline',
        'document_type', 'klass',
        'contract_number', 'originator', 'leader', 'approver',
        'engineering_phase', 'feed_update', 'system', 'wbs',
        'under_contractor_review', 'under_ca_review', 'created_on',
    )
    for parameter_name in parameter_names:
        parameter = data.get(parameter_name, None)
        if parameter:
            advanced_args[parameter_name] = parameter

    queryset = queryset.filter(**advanced_args)

    # Special case of advanced filtering with a text field
    cdn = data.get('contractor_document_number', None)
    if cdn:
        queryset = queryset.filter(
            contractor_document_number__icontains=cdn
        )

    return queryset


# HACK to fix http://hg.python.org/cpython/rev/4f0988e8fcb1/
class FixedZipFile(zipfile.ZipFile):
    """Old versions of Python don't have the patch merged."""
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()


def compress_documents(documents, format='both', revisions='latest'):
    """Compress the given files' documents (or queryset) in a zip file.

    * format can be either 'both', 'native' or 'pdf'
    * revisions can be either 'latest' or 'all'

    Returns the name of the ziped file.
    """
    temp_file = tempfile.TemporaryFile()

    with FixedZipFile(temp_file, mode='w') as zip_file:
        files = []
        for document in documents:
            if revisions == 'latest':
                revs = [document.latest_revision()]
            elif revisions == 'all':
                revs = document.documentrevision_set.all()

            for rev in revs:
                if rev is not None:
                    if format in ('native', 'both'):
                        files.append(rev.native_file)
                    if format in ('pdf', 'both'):
                        files.append(rev.pdf_file)

        for file_ in files:
            if file_.name:
                zip_file.write(
                    file_.path,
                    file_.name,
                    compress_type=compression
                )
    return temp_file
