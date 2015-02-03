# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import re
import logging

from core.celery import app

from documents.models import Document


logger = logging.getLogger(__name__)


# Revision file names come from ``documents/fileutils.py``
# <document_key>_<revision>.<extension>
revfile_re = re.compile('(?P<document_key>[\w-]+)_(?:0+)?(?P<revision>\d+).(?P<extension>\w+)')


@app.task
def import_file(filename):
    logger.info('Trying to import file "%s"' % filename)

    basename = os.path.basename(filename)
    match = revfile_re.match(basename)

    if match is None:
        logger.warning('"%s" does not follows naming convention' % basename)

    document_key = match.group('document_key')
    revision = match.group('revision')
    extension = match.group('extension')

    document = Document.objets.get(document_key=document_key)



    # Check extension to know if it's native_file or pdf_file
    # Fetch related document
    # check if field is already filled
    # If not, set the field
    # save document
    print filename
