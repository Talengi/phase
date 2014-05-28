# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible

import csv
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django_extensions.db.fields import UUIDField
from model_utils import Choices

from categories.models import Category
from documents.models import Document
from documents.forms.models import documentform_factory
from documents.utils import create_document_from_forms


class normal_dialect(csv.Dialect):
    delimiter = b';'
    quotechar = b'"'
    doublequote = False
    skipinitialspace = True
    lineterminator = b'\r\n'
    quoting = csv.QUOTE_NONE
    strict = True
csv.register_dialect('normal', normal_dialect)


@python_2_unicode_compatible
class ImportBatch(models.Model):
    STATUSES = Choices(
        ('new', _('New')),
        ('started', _('Started')),
        ('success', _('Success')),
        ('partial_success', _('Partial success')),
        ('error', _('Error')),
    )

    uid = UUIDField(primary_key=True)
    category = models.ForeignKey(
        Category,
        verbose_name=_('Category')
    )
    file = models.FileField(
        _('File'),
        upload_to='import_%Y%m%d'
    )
    status = models.CharField(
        _('Status'),
        max_length=50,
        choices=STATUSES,
        default=STATUSES.new
    )

    class Meta:
        verbose_name = _('Import batch')
        verbose_name_plural = _('Import batches')

    @property
    def imported_type(self):
        return self.category.category_template.metadata_model

    def __str__(self):
        return 'Import {} ({})'.format(self.uid, self.imported_type)

    def get_absolute_url(self):
        return reverse('import_status', args=[self.uid])

    def get_form_class(self):
        form_class = documentform_factory(self.imported_type.model_class())
        return form_class

    def get_form(self, data=None):
        return self.get_form_class()(data)

    def get_revisionform_class(self):
        obj_class = self.imported_type.model_class()
        obj = obj_class()
        form_class = documentform_factory(obj.get_revision_class())
        return form_class

    def get_revisionform(self, data=None):
        return self.get_revisionform_class()(data)

    def __iter__(self):
        """Loop over csv data."""
        with open(self.file.path, 'rb') as f:
            csvfile = csv.DictReader(f, dialect='normal')
            for row in csvfile:
                imp = Import(batch=self, data=row)
                yield imp

    def do_import(self):
        for imp in self:
            imp.do_import()


class Import(models.Model):
    batch = models.ForeignKey(
        ImportBatch,
        verbose_name=_('Batch')
    )
    document = models.ForeignKey(
        Document,
        null=True, blank=True
    )

    def __init__(self, *args, **kwargs):
        self.data = kwargs.pop('data', None)
        super(Import, self).__init__(*args, **kwargs)

    def get_forms(self):
        return (
            self.batch.get_form(self.data),
            self.batch.get_revisionform(self.data)
        )

    def do_import(self):
        assert hasattr(self, 'data')

        form, revision_form = self.get_forms()
        if form.is_valid() and revision_form.is_valid():
            doc, metadata, revision = create_document_from_forms(
                form, revision_form, self.batch.category, draft=True)
            self.document = doc
