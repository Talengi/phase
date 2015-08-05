# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import re

from documents.models import Document


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

    def get_validators(self):
        return self.VALIDATORS

    def validate(self, obj):
        errors = dict()
        for validator in self.get_validators():
            error = validator.validate(obj)
            if error:
                errors.update(error)

        if errors:
            return {self.error_key: errors}
        else:
            return None


class AndValidator(Validator):
    """A validator that stops when a single validation fail."""

    def get_validators(self):
        return self.VALIDATORS

    def validate(self, obj):
        for validator in self.get_validators():
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


class TrsExistenceValidator(Validator):
    """Checks that the corresponding trs does not already exist."""
    error = 'The current transmittal already exist'
    error_key = 'already_exists'

    def test(self, trs_import):
        from transmittals.models import Transmittal
        name = trs_import.basename
        qs = Transmittal.objects \
            .filter(document_key=name) \
            .filter(status__in=['new', 'tobechecked', 'accepted'])
        return qs.count() == 0


class TrsSequentialNumberValidator(Validator):
    """Checks that the sequential number is correct."""
    error = 'The sequential number is incorrect'
    error_key = 'wrong_sequential_number'

    def test(self, trs_import):
        """Check that the previous trs exists."""
        from transmittals.models import Transmittal
        name = trs_import.basename
        split = name.split('-')

        # Directory name is incorrect, let's just ignore this test
        if len(split) != 5:
            return True

        contract_number, originator, recipient, _, seq_number = split

        # The sequential error is not an int, ignore this test
        try:
            seq_number = int(seq_number)
        except ValueError:
            return True

        # If first transmittal of the sequence, there is
        # no previous transmittal obviously
        if seq_number == 1:
            return True

        qs = Transmittal.objects \
            .filter(contract_number=contract_number) \
            .filter(originator=originator) \
            .filter(recipient=recipient) \
            .filter(sequential_number=seq_number - 1) \
            .exclude(status='rejected')
        return qs.count() == 1


class CSVPresenceValidator(Validator):
    """Checks the existance of the transmittals csv file."""
    error = 'The csv file is missing, or it\'s name is incorrect'
    error_key = 'missing_csv'

    def test(self, trs_import):
        csv_fullname = trs_import.csv_fullname
        return os.path.exists(csv_fullname)


class CSVColumnsValidator(Validator):
    """Checks that the csv columns are correct."""
    error = 'The csv columns are incorrect.'
    error_key = 'csv_columns'

    def test(self, trs_import):
        columns = set(trs_import.csv_cols())
        expected_columns = set(trs_import.expected_columns().values())
        return columns == expected_columns


class PdfCountValidator(Validator):
    """Checks the number of pdf documents."""
    error = 'The number of pdf documents is incorrect'
    error_key = 'wrong_pdf_count'

    def test(self, trs_import):
        csv_lines = trs_import.csv_lines()
        pdf_names = trs_import.pdf_names()

        return len(csv_lines) == len(pdf_names)


class NativeFileValidator(Validator):
    """Checks that every file correspond to a line in the csv."""
    error = 'This file should not be there'
    error_key = 'native_files'

    def validate(self, trs_import):
        """

        The only thing we have to do to know if the file must be here is to
        check if the corresponding pdf exists.

        """
        native_files = trs_import.native_names()
        pdf_files = trs_import.pdf_names()
        errors = dict()

        for filename in native_files:
            name, ext = os.path.splitext(filename)
            pdf_name = '%s.pdf' % name
            if pdf_name not in pdf_files:
                errors[filename] = self.error

        if errors:
            return {self.error_key: errors}
        else:
            return None


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


class RevisionFormatValidator(Validator):
    """Checks that the revision is a two number integer."""
    pattern = '\d{2}'
    error = 'The revision must be a two number integer'
    error_key = 'revision_format'

    def test(self, import_line):
        revision = import_line.csv_data['revision']
        return re.match(self.pattern, revision)


class DocumentExistsValidator(Validator):
    """Checks that the document already exists in Phase."""
    error = 'The corresponding document cannot be found.'
    error_key = 'document_not_found'

    def test(self, import_line):
        return import_line.get_metadata() is not None


class DocumentCategoryValidator(Validator):
    """Checks that the document belongs to the same category as the transmittal."""
    error = 'The transmittal and document categories do not match.'
    error_key = 'wrong_category'

    def test(self, import_line):
        metadata = import_line.get_metadata()

        # If the document does not exist, we cannot perform this test
        if metadata is None:
            return True

        return metadata.document.category == import_line.trs_import.doc_category


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
        metadata = import_line.get_metadata()
        if not metadata:
            return True

        return metadata.title == import_line.csv_data['title']


class CSVLineValidator(AndValidator):
    """Validate the csv content.

    This validator is designed to be fired on every csv line. Checks that:
      * the data is valid (form validation)
      * the pdf is present with the correct name
      * the document already exists in Phase
      * the title is the same as in the existing document

    """
    error_key = 'csv_content'
    VALIDATORS = (
        MissingDataValidator(),
        RevisionFormatValidator(),
        PdfFilenameValidator(),
        DocumentCategoryValidator(),
        SameTitleValidator(),
        FormValidator(),
    )


class TrsValidator(CompositeValidator):
    """Global validator for the transmittals."""
    error_key = 'global_errors'
    VALIDATORS = (
        DirnameValidator(),
        TrsExistenceValidator(),
        TrsSequentialNumberValidator(),
        CSVPresenceValidator(),
        CSVColumnsValidator(),
        PdfCountValidator(),
        NativeFileValidator()
    )


class RevisionsValidator(Validator):
    """Global revision number validator."""
    error_key = 'revisions'

    def validate(self, trs_import):
        """Validate the revision numbers.

        Multiple revisions of the same document can be created
        in a single csv.

        Because of that, we need to check that all the revisions
        to create will have following numbers.

        """
        errors = dict()

        # Let's store the list of revisions for each document
        revisions = dict()
        for line in trs_import.csv_lines():
            document_key = line['document_key']
            revision = int(line['revision'])

            if document_key not in revisions:
                revisions[document_key] = list()

            revisions[document_key].append(revision)

        # Get latest revision for each document
        latest_revisions = Document.objects \
            .filter(document_key__in=revisions.keys) \
            .values_list('document_key', 'current_revision')
        latest_revisions = dict(latest_revisions)

        # Check revisions for each document
        for document_key in revisions.keys():
            revision_ids = revisions[document_key]
            latest_revision = latest_revisions.get(document_key, -1)
            revision_errors = self._validate_revision(revision_ids, latest_revision)

            if revision_errors:
                errors[document_key] = revision_errors

        if errors:
            return {self.error_key: errors}
        else:
            return errors

    def _validate_revision(self, revisions, latest_revision):
        """Check the revision numbers for a single document."""
        errors = dict()
        revisions.sort()
        previous_revision = latest_revision
        for revision in revisions:
            if revision < 0:
                errors[revision] = '%d is not a valid revision number' % revision
            elif revision > previous_revision + 1:
                errors[revision] = '%d is missing some previous revisions' % revision

            if revision > latest_revision:
                previous_revision = revision

        return errors
