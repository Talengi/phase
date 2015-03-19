# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging

from core.celery import app


logger = logging.getLogger(__name__)


@app.task
def process_transmittal(transmittal_id):
    logger.info('Starting to process transmittal {}'.format(transmittal_id))
