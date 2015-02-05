# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import csv

from trsimports.validation import TrsValidator


class TrsImport(object):
    """A transmittals import encapsulation."""

    def __init__(self, trs_dir, tobechecked_dir, accepted_dir, rejected_dir):
        self.trs_dir = trs_dir
        self.tobechecked_dir = tobechecked_dir
        self.accepted_dir = accepted_dir
        self.rejected_dir = rejected_dir

        self._errors = None

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
        try:
            with open(self.csv_fullname, 'rb') as f:
                csvfile = csv.DictReader(f, dialect='normal')
                lines = [row for row in csvfile]
        except IOError:
            # If no csv file is found, we just return an empty list
            # The csv existence will raise an error during validation anyway
            lines = list()

        return lines

    def pdf_names(self):
        """Returns the list of pdf files."""
        files = os.listdir(self.trs_dir)
        pdfs = [f for f in files if f.endswith('pdf')]
        return pdfs

    @property
    def errors(self):
        if self._errors is None:
            self.validate()
        return self._errors

    def validate(self):
        """Performs a full automatic validation of the transmittals."""
        validator = TrsValidator()
        self._errors = validator.validate(self)
