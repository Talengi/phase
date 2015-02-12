# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import csv
import shutil
import logging

from annoying.functions import get_object_or_None

from trsimports.validation import (
    TrsValidator, CSVLineValidator, RevisionsValidator)
from trsimports.reports import ErrorReport


logger = logging.getLogger(__name__)


class TrsImport(object):
    """A transmittals import encapsulation.

    We don't perform verifications on the existence and permissions
    of the different directories.

    Those verifications must be performed upwards, e.g in the management command.

    """
    def __init__(self, trs_dir, tobechecked_dir, accepted_dir, rejected_dir, email_list):
        self.trs_dir = trs_dir
        self.tobechecked_dir = tobechecked_dir
        self.accepted_dir = accepted_dir
        self.rejected_dir = rejected_dir
        self.email_list = email_list

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
        """Returns the expected csv columns.

        In the end, it should depend on the document category,
        but for now it's just a fixed requirement.

        """
        return ('document_key', 'title', 'contract_number', 'originator',
                'unit', 'discipline', 'document_type', 'sequential_number',
                'docclass', 'revision', 'status', 'revision_date',)

    def csv_cols(self):
        """Returns the coloumns of the csv."""
        if not self._csv_cols:
            try:
                line = self.csv_lines()[0]
                self._csv_cols = line.keys()
            except:
                self._csv_cols = []

        return self._csv_cols

    def csv_lines(self):
        """Returns a list of lines contained in the csv file."""
        if not self._csv_lines:
            try:
                with open(self.csv_fullname, 'rb') as f:
                    csvfile = csv.DictReader(f, dialect='normal')
                    lines = [row for row in csvfile]
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
        self._errors = dict()
        self._validate_transmittal()
        self._validate_csv_content()

        # We need a valid transmittals to check revision numbers
        if not self._errors:
            self._validate_revisions()

    def _validate_transmittal(self):
        errors = TrsValidator().validate(self)
        if errors:
            self._errors.update(errors)

    def _validate_csv_content(self):
        errors = dict()
        line_nb = 1
        for import_line in self:
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
        errors = RevisionsValidator().validate(self)
        if errors:
            self._errors.update(errors)


class TrsImportLine(object):
    """A single line of the transmittal."""

    def __init__(self, csv_data, trs_import):
        self.csv_data = csv_data
        self.trs_import = trs_import
        self.trs_dir = trs_import.trs_dir

        self._errors = None
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
        return '%s_%02d_%s.pdf' % (
            self.csv_data['document_key'],
            int(self.csv_data['revision']),
            self.csv_data['status']
        )

    @property
    def pdf_fullname(self):
        return os.path.join(self.trs_dir, self.pdf_basename)

    def get_metadata_class(self):
        from default_documents.models import ContractorDeliverable
        return ContractorDeliverable

    def get_metadata(self):
        if self._metadata is None:
            qs = self.get_metadata_class().objects \
                .select_related('document', 'latest_revision')
            self._metadata = get_object_or_None(
                qs,
                document__document_key=self.csv_data['document_key'])

        return self._metadata

    def get_metadata_form_class(self):
        from default_documents.forms import ContractorDeliverableForm
        return ContractorDeliverableForm

    def get_revision_form_class(self):
        from default_documents.forms import ContractorDeliverableRevisionForm
        return ContractorDeliverableRevisionForm

    def get_forms(self):
        """Returns the bound forms.

        The document MUST exist in the database.

        """
        metadata = self.get_metadata()

        MetadataForm = self.get_metadata_form_class()
        metadata_form = MetadataForm(self.csv_data, instance=metadata)

        revision_num = self.csv_data['revision']
        revision = metadata.get_revision(revision_num)

        RevisionForm = self.get_revision_form_class()
        revision_form = RevisionForm(self.csv_data, instance=revision)

        return metadata_form, revision_form
