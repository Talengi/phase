# -*- coding: utf-8 -*-


import logging

from django.core.management.base import BaseCommand

from discussion.models import Note
from discussion.signals import update_cache


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """For each discussion, the discussion length is cached by a post_save
    signal. If necessary, this command updates cache."""
    def handle(self, *args, **options):
        logger.info('Refresh discussion cache count')

        for note in Note.objects.all():
            update_cache(Note, note)
