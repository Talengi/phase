# -*- coding: utf-8 -*-

"""List of all exceptions for the transmittals import feature."""

from __future__ import unicode_literals


class TrsImportError(Exception):
    """Base class for all transmittals import errors."""
    pass


class InvalidDirNameError(TrsImportError):
    """The transmittals directory name is invalid."""
    pass
