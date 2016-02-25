from random import choice

from django.db import transaction

from documents.factories import DocumentFactory
from default_documents.factories import MetadataRevisionFactory
from default_documents.models import DemoMetadata


@transaction.atomic
def generate_random_documents(nb_of_docs, category):
    """Generate a bunch of random documents.

    This function is useful for testing purpose.

    """
    if category.category_template.metadata_model.model_class() != DemoMetadata:
        error_message = ('This function is only useful for testing purpose. '
                         'The category you pass as an argument can only host '
                         'documents of the DemoMetadata type.')
        raise Exception(error_message)

    for i in range(nb_of_docs):
        document = DocumentFactory(
            category=category,
        )
        metadata = document.get_metadata()
        max_revision = choice(range(1, 5))
        for revision_number in range(2, max_revision):
            MetadataRevisionFactory(
                revision=u"{0:0>2}".format(revision_number),
                revision_date='{year}-{month:0>2}-{day:0>2}'.format(
                    year=2008 + revision_number,
                    month=choice(range(1, 13)),
                    day=choice(range(1, 29)),
                ),
                metadata=metadata
            )
