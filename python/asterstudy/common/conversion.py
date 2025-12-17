# -*- coding: utf-8 -*-

# Copyright 2016 EDF R&D
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
Conversion helper
-----------------

This module provides utilities to help during conversion.

"""


import os.path as osp
import re

from .base_utils import no_new_attributes
from .utilities import get_file_name, to_unicode, translate, wait_cursor

# mark used to identify added lines
MARK = "ASTERSTUDY_IMPORT:"
# mark used to comment inactive Commands
COMMENT = "#comment: "


class FileProvider:
    """This object is used to provide additional files that may be necessary
    during a conversion of a COMM file.

    Default implementation provides a static provider that registers files
    in a dictionnary indexed by a tag. This tag contains the source of the file.
    When requesting a datafile if the source is 'data:' and the file exists in
    the data directory, it is automatically added and provided.

    Arguments:
        datadir (str): Path to a directory containing some files.

    Attributes:
        _files (dict): Store of the files properties as dict.
    """
    _dir = _files = None
    __setattr__ = no_new_attributes(object.__setattr__)

    def __init__(self, datadir):
        self._dir = datadir
        self._files = {}

    def add(self, key, filename):
        """Add an existing file.

        Arguments:
            key (misc): Key to identify the file.
            filename (str): Path to the referenced file.
        """
        self._files[key] = filename

    def is_available(self, key):
        """Tell if a file is registered with this *key*.

        Arguments:
            key (misc): Key to identify the file.

        Returns:
            bool: *True* a such file is available, *False* otherwise.
        """
        if key in self._files:
            return True

        typ, value = str(key).split(':')
        if typ == 'data':
            path = osp.join(self._dir, value)
            if osp.isfile(path):
                self.add(key, path)

        return key in self._files

    def filename(self, key):
        """Returns the filename of an expected file.

        Arguments:
            key (misc): Key to identify the file.

        Returns:
            str: Name of the file or *None* if it isn't found.
        """
        return self._files[key]

    def content(self, key):
        """Returns the content of an expected file.

        Arguments:
            key (misc): Key to identify the file.

        Returns:
            str: Content of the file.

        Raises:
            KeyError if no file has been found.
        """
        filename = self._files[key]
        with open(filename, 'rb') as fobj:
            text = fobj.read()
        return text


class IncludeProvider(FileProvider):
    """Object that asks the user for an INCLUDE file during graphical import.

    Attributes:
        _files (dict): Store of the files properties as dict.
        _window (*QObject*): Parent window of the file browser.
    """
    _window = None
    __setattr__ = no_new_attributes(object.__setattr__)

    def __init__(self, datadir, window):
        super().__init__(datadir)
        self._window = window

    def is_available(self, key):
        """Tell if a file is registered with this *key*.

        If the file is available in the data directory it is directly provided
        without opening the file dialog.

        Arguments:
            key (misc): Key to identify the file.

        Returns:
            bool: *True* a such file is available, *False* otherwise.
        """
        exists = super().is_available(key)
        if exists:
            return exists

        wait_cursor(False)
        typ, value = key.split(':')
        if typ == 'unit':
            from_str = translate("AsterStudy", "on unit {0}")
        else:
            from_str = translate("AsterStudy", "named {0}")
        title = translate("AsterStudy",
                          "Please select a file for INCLUDE {0}"
                          .format(from_str.format(value)))
        file_filter = [translate("AsterStudy", "Command files") + " (*.[0-9]*)",
                       translate("AsterStudy", "All files") + " (*.*)"]
        filename = get_file_name(1, self._window, title, "", file_filter)
        if filename:
            self.add(key, filename)
        wait_cursor(True)
        return super().is_available(key)


class TextProvider(FileProvider):
    """Specific :class:`FileProvider` that also stores the contents instead
    of the filenames.

    Only used in unittests.
    """

    def filename(self, key):
        """Returns the filename of an expected file.

        Arguments:
            key (misc): Key to identify the file.

        Returns:
            str: Pseudo filename.
        """
        return "filename_{0}".format(key)

    def content(self, key):
        """Returns the content of an expected file.

        Arguments:
            key (misc): Key to identify the file.

        Returns:
            str, str: Filename and content of the file.

        Raises:
            KeyError if no file has been found.
        """
        return self._files[key]


class ConversionReport:
    """Store warnings/errors that occurred during a conversion.
    """
    _errors = _warnings = None
    __setattr__ = no_new_attributes(object.__setattr__)

    def __init__(self):
        self._errors = []
        self._warnings = []

    def error(self, exc):
        """Register an error.

        Arguments:
            exc (*ConversionError*): Exception raised during conversion.
        """
        self._errors.append(exc)

    def warn(self, msg):
        """Register a warning.

        Arguments:
            msg (str): Text of the warning message.
        """
        if msg not in self._warnings:
            self._warnings.append(msg)

    def get_errors(self):
        """Returns the text report in a *user friendly* format.

        Returns:
            str: Text report.
        """
        unmark = re.compile(re.escape(MARK) + ' *')
        text = []
        for error in self._errors:
            exc = error.original_exception
            # the original exception may be a string (invalid syntax)
            exc_args = getattr(exc, "args", [to_unicode(exc)])
            msg = "".join([to_unicode(i) for i in exc_args])
            msg = unmark.sub("", msg).strip()
            if isinstance(exc, NotImplementedError):
                text_i = ("Error near the line {0._lineno}:\n"
                          "{1}").format(error, msg)
            else:
                text_i = ("{2.__class__.__name__}, near the line {0._lineno}:\n"
                          "{1}\n\n"
                          "Line is: {0._line}").format(error, msg, exc)
            text.append(text_i)
        return "\n".join(text)

    def iter_warnings(self, count=5):
        """Iterator on the warnings message."""
        for msg in self._warnings[:count]:
            yield msg
        if len(self._warnings) > count:
            yield (translate("AsterStudy",
                             "Only first {0} warnings out of {1} have been "
                             "reported.")
                   .format(count, len(self._warnings)))

    def get_warnings(self):
        """Returns the text report of all warnings.

        Returns:
            str: Text report.
        """
        return "\n".join(self.iter_warnings())
