# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import csv
import shutil
import logging
import glob
import datetime

from django.db import transaction
from django.core.files import File

from annoying.functions import get_object_or_None

from documents.models import Document
from documents.utils import save_document_forms
from transmittals.validation import (
    TrsValidator, CSVLineValidator, RevisionsValidator)
from transmittals.reports import ErrorReport


logger = logging.getLogger(__name__)


class TrsImport(object):
    """A transmittals import encapsulation.

    We don't perform verifications on the existence and permissions
    of the different directories.

    Those verifications must be performed upwards, e.g in the management command.

    """
    def __init__(self, trs_dir, tobechecked_dir, accepted_dir, rejected_dir,
                 email_list, contractor, doc_category, trs_category):
        self.trs_dir = trs_dir
        self.tobechecked_dir = tobechecked_dir
        self.accepted_dir = accepted_dir
        self.rejected_dir = rejected_dir
        self.email_list = email_list
        self.contractor = contractor
        self.doc_category = doc_category
        self.trs_category = trs_category

        self._errors = None
        self._csv_cols = None
        self._csv_lines = None
        self._pdf_names = None
        self._native_names = None

    def __iter__(self):
        for line in self.csv_lines():
            import_line = TrsImportLine(line, self)
            yield import_line

    def do_import(self):
        logger.info('Starting import of transmittals %s' % self.basename)
        if not self.is_valid():
            error_report = ErrorReport(self)
            error_report.send()
            self.move_to_rejected()
        else:
            self.save()
            self.move_to_tobechecked()

    def move_to_rejected(self):
        """Move the imported transmittals directory to rejected."""
        new_path = os.path.join(self.rejected_dir, self.basename)
        logger.info('Moving transmittals from %s to %s' % (
            self.trs_dir,
            new_path
        ))

        # If the dir already exists in rejected, it means it was previously
        # submitted and rejected, and the directory was not cleaned.
        # We just erase the old dir.
        if os.path.exists(new_path):
            # WARNING !!!
            # rmtree deletes an entire directory tree. Handle with care.
            # To make sure we won't delete system dir by mistake, we check
            # that new_path has a depth of at least 3
            new_path = os.path.abspath(new_path)
            if new_path.count('/') < 3:
                error = "Cannot delete old rejected transmittal %s" % new_path
                logger.critical(error)
                raise RuntimeError(error)

            shutil.rmtree(new_path)

        os.rename(self.trs_dir, new_path)

    def move_to_tobechecked(self):
        """Move the imported transmittals directory to tobechecked."""
        new_path = os.path.join(self.tobechecked_dir, self.basename)
        logger.info('Moving transmittals from %s to %s' % (
            self.trs_dir,
            new_path
        ))

        # If the dir already exists in tobechecked, it means we are accepting
        # the same transmittal twice. It cannot happen.
        if os.path.exists(new_path):
            error = "Transmittal %s already exists" % self.basename
            logger.critical(error)
            raise RuntimeError(error)

        os.rename(self.trs_dir, new_path)

    def is_valid(self):
        return not bool(self.errors)

    @property
    def basename(self):
        return os.path.basename(self.trs_dir)

    @property
    def csv_fullname(self):
        return os.path.join(self.trs_dir, '%s.csv' % self.basename)

    @property
    def csv_basename(self):
        return os.path.basename(self.csv_fullname)

    def expected_columns(self):
        """Returns the expected csv columns."""
        return self.doc_category.get_transmittal_columns()

    def csv_cols(self):
        """Returns the colomns of the csv."""
        if not self._csv_cols:
            try:
                line = self.csv_lines()[0]
                self._csv_cols = line.keys()
            except:
                self._csv_cols = []

        return self._csv_cols

    def csv_lines(self):
        """Returns a list of lines contained in the csv file.

        The csv columns title are the human version, e.g "Document Number"
        instead of "document_key".

        We need to do the conversion ourselves.

        """
        if not self._csv_lines:
            columns = self.expected_columns()
            try:
                with open(self.csv_fullname, 'rb') as f:
                    csvfile = csv.DictReader(f, dialect='normal')
                    lines = []
                    for row in csvfile:
                        line_row = {}
                        for key, value in row.items():
                            line_row[columns.get(key, key)] = value or None

                        lines.append(line_row)
            except IOError:
                # If no csv file is found, we just return an empty list
                # The csv existence will raise an error during validation anyway
                lines = list()

            self._csv_lines = lines
        return self._csv_lines

    def pdf_names(self):
        """Returns the list of pdf files."""
        if not self._pdf_names:
            files = os.listdir(self.trs_dir)
            self._pdf_names = [f for f in files if f.endswith('pdf')]

        return self._pdf_names

    def native_names(self):
        """Returns the list of native files."""
        if not self._native_names:
            files = os.listdir(self.trs_dir)
            self._native_names = [f for f in files if (not f.endswith('pdf')) and f != self.csv_basename]

        return self._native_names

    @property
    def errors(self):
        if self._errors is None:
            self.validate()
        return self._errors

    def validate(self):
        """Performs a full automatic validation of the transmittals."""
        logger.info('Starting validation of transmittal %s' % self.basename)

        self._errors = dict()
        self._validate_transmittal()
        self._validate_csv_content()

        # We need a valid transmittals to check revision numbers
        if not self._errors:
            self._validate_revisions()

    def _validate_transmittal(self):
        logger.info('Validating transmittal')

        errors = TrsValidator().validate(self)
        if errors:
            self._errors.update(errors)

    def _validate_csv_content(self):
        logger.info('Validating csv content')

        errors = dict()
        line_nb = 1
        for import_line in self:
            if line_nb % 100 == 0:
                logger.info('Validating line {}'.format(line_nb))

            line_errors = import_line.errors
            if line_errors:
                # n + 1 because we need to take the first line (col definition)
                # into account
                errors.update({line_nb + 1: line_errors})
            line_nb += 1

        if errors:
            self._errors['csv_content'] = errors

    def _validate_revisions(self):
        """Check that revision numbers are correct."""
        logger.info('Validating revisions')

        errors = RevisionsValidator().validate(self)
        if errors:
            self._errors.update(errors)

    @property
    def contract_number(self):
        return self.basename.split('-')[0]

    @property
    def originator(self):
        return self.basename.split('-')[1]

    @property
    def recipient(self):
        return self.basename.split('-')[2]

    @property
    def sequential_number(self):
        return int(self.basename.split('-')[4])

    @transaction.atomic
    def save(self):
        """Save transmittal data in db."""

        # We import those here because we need to make sure that
        # the values_lists have already been populated
        from transmittals.models import TrsRevision
        from transmittals.forms import TransmittalForm, TransmittalRevisionForm

        # Build the list of related documents
        keys = []
        for line in self:
            key = line.csv_data['document_key']
            if key not in keys:
                keys.append(key)
        related_documents = Document.objects \
            .filter(document_key__in=keys) \
            .values_list('id', flat=True)

        data = {
            'contractor': self.contractor,
            'tobechecked_dir': self.tobechecked_dir,
            'accepted_dir': self.accepted_dir,
            'rejected_dir': self.rejected_dir,
            'contract_number': self.contract_number,
            'originator': self.originator,
            'recipient': self.recipient,
            'sequential_number': self.sequential_number,
            'status': 'tobechecked',
            'related_documents': list(related_documents),
            'revision_date': datetime.date.today(),
            'received_date': datetime.date.today(),
            'created_on': datetime.date.today(),
        }

        # The csv file is linked in the "native_file" field
        native_file = File(open(self.csv_fullname))
        files = {
            'native_file': native_file,
        }

        # Use document forms to create the Transmittal
        form = TransmittalForm(data=data)
        revision_form = TransmittalRevisionForm(data=data, files=files)
        doc, transmittal, revision = save_document_forms(
            form, revision_form, self.trs_category, is_indexable=False)

        native_file.close()

        nb_line = 0
        for line in self:
            data = line.csv_data
            metadata = line.get_metadata()
            document = getattr(metadata, 'document', None)

            if nb_line % 100 == 0:
                logger.info('Importing line {} ({})'.format(
                    nb_line + 1, data['document_key']))

            # Is this a revision creation or are we editing an existing one?
            if metadata is None:
                is_new_revision = True
            else:
                latest_revision = metadata.latest_revision.revision
                is_new_revision = bool(int(data['revision']) > latest_revision)

            pdf_file = File(open(line.pdf_fullname))
            native_file = line.native_fullname
            if native_file:
                native_file = File(open(native_file))

            data.update({
                'transmittal': transmittal,
                'document': document,
                'is_new_revision': is_new_revision,
                'category': self.doc_category,
                'pdf_file': pdf_file,
                'native_file': native_file,
                'sequential_number': line.sequential_number,  # XXX Hack
            })
            TrsRevision.objects.create(**data)
            nb_line += 1

            pdf_file.close()
            if hasattr(native_file, 'close'):
                native_file.close()


class TrsImportLine(object):
    """A single line of the transmittal."""

    def __init__(self, csv_data, trs_import):
        self.csv_data = csv_data
        self.trs_import = trs_import
        self.trs_dir = trs_import.trs_dir

        self._errors = None
        self._document = None
        self._metadata = None

    @property
    def errors(self):
        if self._errors is None:
            self.validate()
        return self._errors

    def validate(self):
        self._errors = CSVLineValidator().validate(self)

    @property
    def pdf_basename(self):
        return '%s_%02d.pdf' % (
            self.csv_data['document_key'],
            int(self.csv_data['revision'])
        )

    @property
    def pdf_fullname(self):
        return os.path.join(self.trs_dir, self.pdf_basename)

    @property
    def native_fullname(self):
        """Get the fullname of the native file or None if there isn't one."""
        # Since we don't know the native file extension, we have to perform
        # a search using the `glob` module.
        pdf = self.pdf_fullname
        stripped_name = pdf[0:-4]
        natives = glob.glob('{}*'.format(stripped_name))

        if len(natives) < 1 or len(natives) > 2:
            raise RuntimeError('Oops. Wrong number of files here.')

        if len(natives) == 1:
            # We found only the pdf itself, there is no native file
            return None

        if len(natives) == 2:
            # We found the pdf and the native
            first_extension = natives[0].split('.')[-1]
            if first_extension == 'pdf':
                return natives[1]
            else:
                return natives[0]

    @property
    def sequential_number(self):
        return self.csv_data['document_key'].split('-')[5]

    def get_document(self):
        if self._document is None:
            qs = Document.objects \
                .select_related('category__category_template')
            self._document = get_object_or_None(
                qs,
                document_key=self.csv_data['document_key'])

        return self._document

    def get_metadata(self):
        if self._metadata is None:
            doc = self.get_document()
            if doc is not None:
                self._metadata = doc.metadata

        return self._metadata

    def get_metadata_form_class(self):
        return self.trs_import.doc_category.get_metadata_form_class()

    def get_revision_form_class(self):
        return self.trs_import.doc_category.get_revision_form_class()

    def get_forms(self):
        """Returns the bound forms.

        The document MUST exist in the database.

        """
        metadata = self.get_metadata()

        MetadataForm = self.get_metadata_form_class()
        metadata_form = MetadataForm(self.csv_data, instance=metadata)

        revision_num = self.csv_data['revision']
        revision = metadata.get_revision(revision_num) if metadata else None

        RevisionForm = self.get_revision_form_class()
        revision_form = RevisionForm(self.csv_data, instance=revision)

        return metadata_form, revision_form
