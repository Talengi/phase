# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import re


class Validator(object):
    """An object which purpose is to check a single validation point."""
    error = 'Undefined error'
    error_key = 'undefined_key'

    def test(self, trs_import):
        raise NotImplementedError()

    def validate(self, obj):
        """Performs the validation.

        The `validate` method must return None if the validation passed, or
        a string containing the error message if any.

        """
        if self.test(obj):
            return None
        else:
            return {self.error_key: self.error}


class CompositeValidator(Validator):
    """A compound validator."""

    def validate(self, obj):
        errors = dict()
        for validator in self.VALIDATORS:
            error = validator.validate(obj)
            if error:
                errors.update(error)

        if errors:
            return {self.error_key: errors}
        else:
            return None


class AndValidator(Validator):
    """A validator that stops when a single validation fail."""

    def validate(self, obj):
        for validator in self.VALIDATORS:
            error = validator.validate(obj)
            if error:
                return error

        return None


class DirnameValidator(Validator):
    """Checks the transmittals directory name."""
    error = 'The directory name is incorrect'
    pattern = 'FAC(09001|10005)-\w{3}-\w{3}-TRS-\d{5}'
    error_key = 'invalid_dirname'

    def test(self, trs_import):
        return re.match(self.pattern, trs_import.basename)


class CSVPresenceValidator(Validator):
    """Checks the existance of the transmittals csv file."""
    error = 'The csv file is missing, or it\'s name is incorrect'
    error_key = 'missing_csv'

    def test(self, trs_import):
        csv_fullname = trs_import.csv_fullname
        return os.path.exists(csv_fullname)


class PdfCountValidator(Validator):
    """Checks the number of pdf documents."""
    error = 'The number of pdf documents is incorrect'
    error_key = 'wrong_pdf_count'

    def test(self, trs_import):
        csv_lines = trs_import.csv_lines()
        pdf_names = trs_import.pdf_names()

        return len(csv_lines) == len(pdf_names)


class PdfFilenameValidator(Validator):
    """Checks that the pdf exists."""
    error = 'The pdf for this document is missing.'
    error_key = 'missing_pdf'

    def test(self, import_line):
        return os.path.exists(import_line.pdf_fullname)


class MissingDataValidator(Validator):
    """Checks that the csv data has the minimal required fields."""
    error = 'There are some missing fields in the csv data'
    error_key = 'missing_data'

    def test(self, import_line):
        data = import_line.csv_data
        return all((
            'document_key' in data,
            'revision' in data,
            'status' in data,
            'title' in data,
        ))


class DocumentExistsValidator(Validator):
    """Checks that the document already exists in Phase."""
    error = 'The corresponding document cannot be found.'
    error_key = 'document_not_found'

    def test(self, import_line):
        return import_line.get_metadata() is not None


class FormValidator(Validator):
    """Checks that the submitted data is correct."""
    error = 'The data is incorrect.'
    error_key = 'data_validation'

    def validate(self, import_line):
        document_form, revision_form = import_line.get_forms()
        if document_form.is_valid() and revision_form.is_valid():
            return None
        else:
            errors = dict()
            errors.update(document_form.errors)
            errors.update(revision_form.errors)
            return {self.error_key: errors}


class SameTitleValidator(Validator):
    """Checks that the title in csv is the same as existing document."""
    error = 'The document title is incorrect.'
    error_key = 'wrong_title'

    def test(self, import_line):
        return import_line.get_metadata().title == import_line.csv_data['title']


class RevisionValidator(Validator):
    """Checks that the document revision is correct."""
    error = 'The document revision is incorrect.'
    error_key = 'incorrect_revision'

    def test(self, import_line):
        """The revision in the csv is correct if:

          * the revision already exists
          * the revision immediatley follows the existing latest revision
          * the revision follows a revision that will be created in the csv.

        """
        latest_revision = import_line.get_metadata().latest_revision.revision
        csv_revision = import_line.csv_data['revision']

        return csv_revision >= 1 and csv_revision <= latest_revision + 1


class CSVLineValidator(AndValidator):
    """Validate the csv content.

    This validator is designed to be fired on every csv line. Checks that:
      * the data is valid (form validation)
      * the pdf is present with the correct name
      * the document already exists in Phase
      * the revision already exists, or if it's a new revision…
      * it's number immediatly follows the last revision
      * the title is the same as in the existing document

    """
    error_key = 'csv_content'
    VALIDATORS = (
        MissingDataValidator(),
        PdfFilenameValidator(),
        DocumentExistsValidator(),
        SameTitleValidator(),
        FormValidator(),
        RevisionValidator(),
    )


class TrsValidator(CompositeValidator):
    """Global validator for the transmittals."""
    error_key = 'global_errors'
    VALIDATORS = (
        DirnameValidator(),
        CSVPresenceValidator(),
        PdfCountValidator(),
    )
