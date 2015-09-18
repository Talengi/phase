# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import uuid
import logging

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.module_loading import import_string
from django.http import QueryDict
from django.core.urlresolvers import reverse
from django.conf import settings

from model_utils import Choices

from exports.tasks import process_export


logger = logging.getLogger(__name__)


class Export(models.Model):
    """Represents a document export request."""

    STATUSES = Choices(
        ('new', _('New')),
        ('processing', _('Processing')),
        ('done', _('Done')),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        'accounts.User',
        verbose_name=_('Owner'))
    category = models.ForeignKey(
        'categories.Category',
        verbose_name=_('Category'))
    querystring = models.TextField(
        _('Querystring'),
        blank=True, default='',
        help_text=_('The search filter querystring'))
    status = models.CharField(
        _('Status'),
        max_length=30,
        choices=STATUSES,
        default=STATUSES.new)
    created_on = models.DateTimeField(
        _('Created on'),
        default=timezone.now)

    class Meta:
        app_label = 'exports'
        verbose_name = _('Export')
        verbose_name_plural = _('Exports')

    def get_absolute_url(self):
        return reverse('export_download', args=[self.get_filename()])

    @property
    def format(self):
        """Return the exported file extension."""
        return 'csv'

    def is_ready(self):
        return self.status == self.STATUSES.done

    def get_filters(self):
        """Parse querystring and returns a dict."""
        return QueryDict(self.querystring, mutable=True)

    def get_fields(self):
        """Get the list of fields that must be exported."""
        default_fields = {
            'Document Number': 'document_key',
            'Title': 'title',
        }
        Model = self.category.document_class()
        fields = getattr(Model.PhaseConfig, 'export_fields', default_fields)
        return fields

    def get_filename(self):
        return 'export_{time:%Y%m%d}_{uuid}.{exten}'.format(
            time=self.created_on,
            uuid=self.id,
            exten=self.format)

    def get_url(self):
        return os.path.join(
            settings.EXPORTS_URL.lstrip('/'),
            self.get_filename())

    def get_filepath(self):
        return os.path.join(
            settings.PRIVATE_ROOT,
            settings.EXPORTS_SUBDIR,
            self.get_filename())

    def start_export(self, async=True):
        """Asynchronously starts the export"""
        logger.info('Starting import {}'.format(self.id))

        if async:
            process_export.delay(unicode(self.pk))
        else:
            process_export(unicode(self.pk))

    def write_file(self):
        """Generates and write the file."""
        data_generator = self.get_data_generator()
        formatter = self.get_data_formatter()

        with self.open_file() as the_file:
            for data_chunk in data_generator:
                the_file.write(formatter.format(data_chunk))

        logger.info('Import {} done'.format(self.id))

    def open_file(self):
        """Opens the file in which data should be dumped."""
        return open(self.get_filepath(), 'wb')

    def get_data_generator(self):
        """Returns a generator that yields chunks of data to export."""
        generator_class = 'exports.generators.{}Generator'.format(self.format.upper())
        Generator = import_string(generator_class)
        generator = Generator(self.category, self.get_filters(), self.get_fields())
        return generator

    def get_data_formatter(self):
        """Returns a formatter instance."""
        formatter_class = 'exports.formatters.{}Formatter'.format(self.format.upper())
        Formatter = import_string(formatter_class)
        formatter = Formatter(self.get_fields())
        return formatter
