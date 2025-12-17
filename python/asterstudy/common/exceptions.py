# -*- coding: utf-8 -*-

# Copyright 2017 EDF R&D
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License Version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, you may download a copy of license
# from https://www.gnu.org/licenses/gpl-3.0.

"""
Exceptions
----------

Dedicated exceptions for the AsterStudy application.

"""


from .utilities import translate


class AsterStudyError(Exception):
    """
    Base exception for AsterStudy.

    Attributes:
        _msg (str): the message to display.
        _details (str): more details about the error.
    """
    title = translate("AsterStudy", "Error")

    def __init__(self, msg, details=""):
        super().__init__()
        self._msg = msg
        self._details = details

    @property
    def msg(self):
        """Property that holds the main message."""
        return str(self._msg)

    @property
    def details(self):
        """Property that holds the detailed message."""
        return self._details

    def __str__(self):
        return self.msg

    def for_messagebox(self):
        """Return keywords arguments to create a QMessageBox."""
        return {'title': self.title, 'text': self.msg,
                'detailedText': self.details}


class VersionError(AsterStudyError):
    """Exception raised when there is an inconsistency with code_aster
    versions."""


class AsterStudyInterrupt(AsterStudyError):
    """Same as AsterStudyError exception but with a flag that means that
    the flow was interrupted."""


class StudyDirectoryError(AsterStudyError):
    """
    Exception raised during checking the study directory consistency.
    """
    title = translate("AsterStudy", "Inconsistent study directory")


class MissingStudyDirError(StudyDirectoryError):
    """
    Exception raised during checking the study directory consistency if the
    study directory is missing.
    """
    title = translate("AsterStudy", "Missing study directory")


class ExistingSwapError(AsterStudyError):
    """
    Exception raised at load time when embedded files are found in the
    study directory. Those are normally deleted when the study is close.
    Their presence at load time indicates a suspicion
    that Salome stopped suddenly.
    """
    title = translate("AsterStudy", "Existing embedded files")


class RunnerError(AsterStudyError):
    """Generic exception for errors raised by runners."""
    title = translate("AsterStudy", "Execution error")


class ConversionError(AsterStudyError):
    """Exception raised during conversion.

    Args:
        orig (Exception): Originally raised exception.
        details (str): Original traceback.
        lineo (int): Line number in the text.
        line (str): Last line where the exception was raised.

    Attributes:
        _kind (int): identifier of the error (=CONVERSION).
        _msg (str): the message to display.
        _details (str): Original detailed traceback.
        _orig (Exception): Originally raised exception.
        _lineo (int): Line number in the text.
        _line (str): Last line where the exception was raised.
    """
    title = translate("AsterStudy", "Conversion error")

    def __init__(self, orig, details, lineno, line):
        super().__init__(orig, details)
        self._orig = orig
        self._lineno = lineno
        self._line = line

    @property
    def msg(self):
        """Property that holds the main message."""
        fmt = ("{0._orig.__class__.__name__}: "
               "{0._msg}, near the line {0._lineno}: {0._line!r}")
        return fmt.format(self)

    @property
    def original_exception(self):
        """Property that holds the originally raised exception."""
        return self._orig

class IncludeConversion(AsterStudyError):
    """Exception raised when INCLUDE is found during conversion."""
    title = translate("AsterStudy", "INCLUDE detected")


class CyclicDependencyError(AsterStudyError):
    """Cyclic dependency error."""
    title = translate("AsterStudy", "Cyclic dependency detected")


class CatalogError(AsterStudyError):
    """Generic exception for errors importing a catalog."""
    title = translate("AsterStudy", "Catalog error")

class WritingToExistingFileError(AsterStudyError):
    """Raised when writing to an existing file"""
    title = translate("AsterStudy", "Writing to existing file error")
