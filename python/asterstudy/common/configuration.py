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
Configuration
-------------

This module gives access to the application configuration.

"""


# The pragma below has to be removed after migration to Python 3 and
# suppression of above two lines.
# pragma pylint: disable=wrong-import-position,wrong-import-order

import os
import os.path as osp

from configparser import ConfigParser, Error as ConfigurationError

from .base_utils import get_absolute_path, make_dirs

__all__ = ["CFG", "Configuration", "ConfigurationError"]


RCFILE = "AsterStudy.conf"
RCCFG = "AsterStudyConfig"

__ASTER_OLDSTABLE__ = "@ASTER_OLDSTABLE_DIR@" or "@" "ASTER_OLDSTABLE_DIR" "@"
__ASTER_STABLE__ = "@ASTER_STABLE_DIR@" or "@" "ASTER_STABLE_DIR" "@"
__ASTER_TESTING__ = "@ASTER_TESTING_DIR@" or "@" "ASTER_TESTING_DIR" "@"
__FORCE_SALOMEMECA__ = "@ASTER_FORCE_SALOMEMECA@" or "No"
__DEFAULT_WCKEY__ = "@DEFAULT_WCKEY@" or None
__VERSION_LABEL__ = "@ASTERSTUDY_VERSION_LABEL@" or ""

URL_TRANSLATOR = "http://code-aster.org/spip.php?article1015"


class Configuration:
    """Object to manage the configuration.

    Note:
        The installation parameters are available as attributes and through the
        DEFAULT section.
        This allows to use magic interpolation feature (see `ConfigParser` object).
        For example::

            [Versions]
            stable = %(installdir)/stable
    """

    __slots__ = (
        # internal attribute
        '_cfg', '_defaults',
        # automatically set from the installation
        'installdir', 'rcdir', 'docdir', 'htmldoc',
        'apprc', 'userrc', 'is_installed',
        # change by the application during execution time
        'default_version',
    )

    def __init__(self, user_only=False):
        #: directory name containing the main package 'asterstudy'
        self.installdir = get_absolute_path(osp.join(osp.dirname(__file__),
                                                     os.pardir, os.pardir))
        #: boolean flag: signals that application is properly installed
        self.is_installed = not osp.exists(osp.join(self.installdir, "resources"))
        #: install root directory (valid only if asterstudy runs from install folder)
        root = osp.join(*([self.installdir] + 3 * [os.pardir]))
        #: directory containing the resources files
        self.rcdir = _get_path_from(
            osp.join(self.installdir, "resources"),
            osp.join(root, "share", "salome", "resources", "asterstudy"),
            osp.join(root, "share", "resources", "asterstudy"))
        #: main documentation file
        self.htmldoc = _get_path_from(
            osp.join(self.installdir, "docs", "_build", "html", "index.html"),
            osp.join(root, "share", "doc", "salome", "gui", "ASTERSTUDY", "html", "index.html"),
            osp.join(root, "share", "doc", "asterstudy", "html", "index.html"))
        # dir with extra docs
        doc_file = _get_path_from(
            osp.join(self.installdir, "COPYING"),
            osp.join(root, "share", "doc", "salome", "gui", "ASTERSTUDY", "COPYING"),
            osp.join(root, "share", "doc", "asterstudy", "COPYING"))
        self.docdir =  ''
        #: resource file of the application
        self.apprc = ''
        #: user resource file
        path = osp.join(os.getenv("HOME", "/"), ".config", "salome")
        self.userrc = ''
        make_dirs(path)

        self._defaults = {
            'installdir': self.installdir,
            'rcdir': self.rcdir,
            'docdir': self.docdir,
            'htmldoc': self.htmldoc,
            'apprc': self.apprc,
            'userrc': self.userrc,
            'default_version': 'stable',
        }
        # storage of the configuration parameters
        self._cfg = ConfigParser()
        self._cfg.optionxform = lambda opt: opt
        self._load(user_only)
        #: store default code_aster version
        try:
            self.default_version = self.get("General", "default_version")
        except KeyError:
            self.default_version = None

    def get(self, section, option, raw=False):
        """Get option's value. This is a wrapper on ConfigParser's method."""
        try:
            return self._cfg.get(section, option, raw=raw, vars=self._defaults)
        except ConfigurationError as exc:
            raise KeyError(str(exc)) from exc

    def __getattr__(self, attrname):
        """Wrapper on ConfigParser object"""
        # unknown Configuration attributes are supposed to be attributes of ConfigParser
        return getattr(self._cfg, attrname)

    def _load(self, user_only=False):
        """Load the content of resources files"""
        files = []
        if not user_only:
            files.append(self.apprc)
            paths = os.getenv(RCCFG, '').split(os.pathsep)
            for path in reversed([i for i in paths if i]):
                cfg_file = osp.join(path, RCFILE)
                if osp.exists(cfg_file):
                    files.append(cfg_file)
        if osp.isfile(self.userrc):
            files.append(self.userrc)

        self._cfg.read(files)

        if not user_only:
            # custom initialization from SalomeMeca
            self._force_salomemeca_versions()

    def rcfile(self, filename, must_exist=True):
        """Return the full path to the given resource file.

        Arguments:
            filename (str): Basename of an existing file in the resource
                directory.

        Returns:
            str: Full path to the file or *None* if the file does not exist
                and `must_exist` is *False*.
        """
        path = osp.join(self.rcdir, filename)
        return path if osp.exists(path) or not must_exist else None

    def _force_salomemeca_versions(self):
        """Initialize code_aster versions from SalomeMeca."""
        salomemeca_versions = ["OLDSTABLE", "STABLE", "TESTING", "DEV"]
        for version in salomemeca_versions:
            var_name = "__ASTER_{0}__".format(version)
            var_defval = ("@" "ASTER_{0}_DIR" "@").format(version)
            var_value = globals().get(var_name, var_defval)
            if var_value != var_defval:
                version_root = var_value
            elif (__FORCE_SALOMEMECA__.lower() == "yes" or
                  os.getenv("FORCE_SALOMEMECA", "").lower() == "yes"):
                version_root = os.getenv("ASTER_{0}".format(version))
            else:
                version_root = None
            label = version.lower()
            if os.getenv('DEBUG'):
                print("AsterStudy: config: version: {0}, path : {1}" \
                      .format(label, version_root))
            if version_root:
                version_path = osp.join(version_root, "lib", "aster")
                if osp.isdir(osp.join(version_path, "code_aster")):
                    self.set("Versions", label, version_path)
                    if os.getenv('DEBUG'):
                        print("AsterStudy: add version: {0}, path : {1}" \
                              .format(label, version_path))

    @staticmethod
    def get_wckey():
        """Return the Workload Characterization Key.

        It uses the SLURM_WCKEY environment variable if defined.
        Otherwise, it takes the value set during installation in this file.

        Returns:
            str: Key to be used for SALOME jobs.
        """
        # see `salome_runner` for usages
        defval = ("@" + "DEFAULT_WCKEY" + "@")
        value = __DEFAULT_WCKEY__ if __DEFAULT_WCKEY__ != defval else None
        value = os.getenv("SLURM_WCKEY") or value
        return value

    @staticmethod
    def business_translation_url():
        """Return the url of the business-oriented language translator."""
        return URL_TRANSLATOR

    @staticmethod
    def version_label():
        """Return the version label shown to the user.

        Returns:
            str: The "user" version or "" if it is not defined.
        """
        return __VERSION_LABEL__.replace('@ASTERSTUDY_VERSION_LABEL@', '')


def _get_path_from(*paths):
    for path in paths:
        if osp.exists(path):
            return get_absolute_path(path)
    return None

#: singleton instance of Configuration
CFG = Configuration()
