# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from model_utils import Choices

from exports.tasks import process_export


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

    @property
    def format(self):
        """Return the exported file extension."""
        return 'csv'

    def get_filename(self):
        return 'export_{time:%Y%m%d}_{uuid}.{exten}'.format(
            time=self.created_on,
            uuid=self.id,
            exten=self.format)

    def start_export(self):
        """Asynchronously starts the export"""
        self.status = self.STATUSES.processing
        self.save()

        process_export.delay(self.pk)

    def write_file(self):
        """Generates and write the file."""
        with self.open_file() as the_file:
            data_generator = self.get_data_generator()
            for data_chunk in data_generator:
                the_file.write(data_chunk)

    def open_file(self):
        """Opens the file in which data should be dumped."""
        pass

    def get_data_generator(self):
        """Returns a generator that yields chunks of data to export."""
        pass
