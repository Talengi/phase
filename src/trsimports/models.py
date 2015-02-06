# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import csv

from annoying.functions import get_object_or_None

from trsimports.validation import TrsValidator, CSVLineValidator


class TrsImport(object):
    """A transmittals import encapsulation."""

    def __init__(self, trs_dir, tobechecked_dir, accepted_dir, rejected_dir):
        self.trs_dir = trs_dir
        self.tobechecked_dir = tobechecked_dir
        self.accepted_dir = accepted_dir
        self.rejected_dir = rejected_dir

        self._errors = None
        self._csv_lines = None
        self._pdf_names = None

    def __iter__(self):
        for line in self.csv_lines():
            import_line = TrsImportLine(line, self.trs_dir)
            yield import_line

    def do_import(self):
        pass

    def is_valid(self):
        return not bool(self.errors)

    @property
    def basename(self):
        return os.path.basename(self.trs_dir)

    @property
    def csv_fullname(self):
        return os.path.join(self.trs_dir, '%s.csv' % self.basename)

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


class TrsImportLine(object):
    """A single line of the transmittal."""

    def __init__(self, csv_data, trs_dir):
        self.csv_data = csv_data
        self.trs_dir = trs_dir

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

        RevisionForm = self.get_revision_form_class()
        revision_form = RevisionForm(self.csv_data, instance=metadata.latest_revision)

        return metadata_form, revision_form
