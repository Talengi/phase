import zipfile
import tempfile
try:
    import zlib  # noqa
    compression = zipfile.ZIP_DEFLATED
except:
    compression = zipfile.ZIP_STORED

from django.db.models import Q


def filter_documents(queryset, data):
    """Filter documents from a queryset given data from DataTables.

    Documentation (lack of is more accurate though):
    http://www.datatables.net/examples/server_side/server_side.html
    """
    model = queryset.model

    # Paging (done at the view level, the whole queryset is still required)

    # Ordering
    queryset = queryset.order_by(data.get('sort_by', 'document_number') or 'document_number')

    # Filtering (search)
    searchable_fields = model.PhaseConfig.searchable_fields
    search_terms = data.get('search_terms', None)
    if search_terms:
        q = Q()
        for field in searchable_fields:

            # does the field belong to the Metadata or the corresponding Revision?
            prefix = ''
            if not field in model._meta.get_all_field_names():
                prefix = 'latest_revision__'

            q.add(Q(**{prefix + '%s__icontains' % field: search_terms}), Q.OR)
        queryset = queryset.filter(q)

    # Filtering (custom fields)
    filter_fields = model.PhaseConfig.filter_fields
    advanced_args = {}
    for parameter_name in filter_fields:

        # does the field belong to the Metadata or the corresponding Revision?
        prefix = ''
        if not parameter_name in model._meta.get_all_field_names():
            prefix = 'latest_revision__'

        parameter = data.get(parameter_name, None)
        if parameter:
            advanced_args[prefix + parameter_name] = parameter

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
                revs = [document.latest_revision]
            elif revisions == 'all':
                revs = document.get_all_revisions()

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
