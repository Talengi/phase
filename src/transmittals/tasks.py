# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging
import os

from django.db import transaction

from core.celery import app
from transmittals.models import Transmittal, TrsRevision


logger = logging.getLogger(__name__)


@app.task
def process_transmittal(transmittal_id):
    """Processing the transmittal requires the following steps:

        - Update all the already existing revisions.
        - Create all the new revisions.
        - Create a new Transmittal document
        - Link all revisions to the Transmittal document
        - Move files into the 'accepted' directory
        - Update the Transmittal object status

    """
    logger.info('Starting to process transmittal {}'.format(transmittal_id))

    transmittal = Transmittal.objects.get(pk=transmittal_id)
    revisions = TrsRevision.objects \
        .filter(transmittal=transmittal) \
        .order_by('revision') \
        .select_related()

    try:
        # Update / create documents in db
        with transaction.atomic():
            for trs_revision in revisions:
                trs_revision.save_to_document()

            transmittal.status = 'accepted'
            transmittal.save()

            transmittal.document.is_indexable = True
            transmittal.document.save()

        # Move to accepted directory
        if os.path.exists(transmittal.full_tobechecked_name):
            try:
                os.rename(transmittal.full_tobechecked_name, transmittal.full_accepted_name)
            except OSError as e:
                logger.error('Cannot move transmittal {} ({})'.format(
                    transmittal, e))
        else:
            # If the directory cannot be found in tobechecked, that's weird but we
            # won't trigger an error
            logger.warning('Transmittal {} files are gone'.format(transmittal))

        success_msg = 'Transmittal {} successfully processed'.format(
            transmittal)
        logger.info(success_msg)
    except Exception as e:
        # There was an error processing one of the revision
        # This MUST not happen, since all error conditions MUST
        # have been eliminated during the initial validation phase
        #
        # Revert the transmittal status back, and log the error is all
        # we can do now.
        error_msg = 'Error processing transmittal {} ({})'.format(
            transmittal, e)
        logger.error(error_msg)

        transmittal.status = 'tobechecked'
        transmittal.save()
