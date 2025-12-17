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
Decoder of messages files
-------------------------

Implementation of objects that extract data from code_aster messages files.

"""


import re
from collections import OrderedDict, namedtuple

import numpy

from .base_utils import to_unicode
from .execution import remove_mpi_prefix
from .utilities import translate


Data = namedtuple('Data', ['key', 'x', 'y', 'title', 'xlabel', 'ylabel'])
Info = namedtuple("Info", ["key", "type", "regexp", "title"])

REGINT = re.compile(r"(?P<value>[\-\+]?[0-9]+) *X?", re.M)
REGFLOAT = re.compile(r"(?P<value>[\-\+]?[0-9]+[0-9\.]+(?:[eE][\-\+]?[0-9]+)?)"
                      r" *X?", re.M)


class AbstractDecoder:
    """Abstract decoder."""

    @classmethod
    def decode(cls, text):
        """Decode the given text.

        Arguments:
            text (str): Text of the messages files.

        Return:
            dict(Data): Ordered dict holding the data extracted from the text.
        """
        raise NotImplementedError


class TimeDecoder(AbstractDecoder):
    """Abstract decoder to extract the time steps."""

    _expr = None

    infos = (
        Info("completion", float, REGFLOAT,
             translate("Dashboard", "Completion")),
        Info("time", float, REGFLOAT, translate("Dashboard", "Time")),
    )

    @classmethod
    def decode(cls, text):
        """Decode the given text.

        Arguments:
            text (str): Text of the messages files.

        Return:
            dict(Data): Ordered dict holding the data extracted from the text.
        """
        data = OrderedDict()
        found = list(cls._expr.finditer(text))
        if not found:
            return data

        cmpl = cls.infos[0].key
        for info in cls.infos:
            valy = numpy.array([info.type(mat.group(info.key))
                                for mat in found if mat.group(info.key)])
            valx = numpy.arange(valy.size)
            if valx.size > 1:
                title = info.title
                if info.key == cmpl or cmpl in data:
                    if info.key == cmpl:
                        perc = valy[-1]
                    else:
                        perc = data[cmpl].y[-1]
                    title = r"{0} ({1:.0f}%)".format(title, perc)

                data[info.key] = Data(x=valx, y=valy,
                                      key=info.key, title=title,
                                      xlabel=None, ylabel=None)
        return data


class NLTimeDecoder(TimeDecoder):
    """Decoder that extract the time steps from STAT_NON_LINE/DYNA_NON_LINE."""

    _expr = re.compile(r"(?:\[ *(?P<completion>[0-9]+)% *\])? *"
                       r"Instant de calcul *: +"
                       r"(?P<time>[\-\+]?[0-9\.]+(?:[eE][\-\+]?[0-9]+)?)",
                       re.M)


class DynaVibraTimeDecoder(TimeDecoder):
    """Decoder that extract the time steps from DYNA_VIBRA."""

    _expr = re.compile(r"(?:\[ *(?P<completion>[0-9]+)% *\])? *"
                       r"Instant calcul.*?: *"
                       r"(?P<time>[\-\+]?[0-9\.]+(?:[eE][\-\+]?[0-9]+)?)",
                       re.M)


class DynaVibraFreqDecoder(TimeDecoder):
    """Decoder that extract the frequencies from DYNA_VIBRA."""

    infos = (
        Info("completion", float, REGFLOAT,
             translate("Dashboard", "Completion")),
        Info("freq", float, REGFLOAT, translate("Dashboard", "Frequency")),
    )
    _expr = re.compile(r"(?:\[ *(?P<completion>[0-9]+)% *\])? *"
                       r"Fr.quence calcul.*?: *"
                       r"(?P<freq>[\-\+]?[0-9\.]+(?:[eE][\-\+]?[0-9]+)?)",
                       re.M)


class ConvergenceDecoder(AbstractDecoder):
    """Decoder that extract the values for the convergence table."""
    _filt = re.compile(r"^( *\|.*\|(?:.*\|)+)$", re.M)

    infos = {
        "ITERATION": Info("iteration", int, REGINT,
                          translate("Dashboard", "Iterations")),
        "RESI_GLOB_RELA": Info("resi_glob_rela", float, REGFLOAT,
                               translate("Dashboard", "Relative residue")),
        "RESI_GLOB_MAXI": Info("resi_glob_maxi", float, REGFLOAT,
                               translate("Dashboard", "Absolute residue")),
        "SUIVI": Info("suivi", float, REGFLOAT,
                      translate("Dashboard", "Value of a degree of freedom")),
    }

    @classmethod
    def decode(cls, text):
        """Decode the given text.

        Arguments:
            text (str): Text of the messages files.

        Return:
            dict(Data): Ordered dict holding the data extracted from the text.
        """
        lines = cls._filt.findall(text)

        separ = re.compile(r" *\| *")
        values = OrderedDict()
        idx = dict()
        for line in lines:
            for i, col in enumerate(separ.split(line)):
                if col in cls.infos:
                    idx[i] = (i, col)
                    continue
                if idx.get(i) is None:
                    continue
                # assign the value to the right column
                info = cls.infos[idx[i][1]]
                mat = info.regexp.search(col)
                if not mat:
                    continue
                value = info.type(mat.group('value'))
                values.setdefault(idx[i], []).append(value)

        isuiv = 0
        data = OrderedDict()
        for index in idx.values():
            info = cls.infos[index[1]]
            valy = numpy.array(values.get(index, []))
            valx = numpy.arange(valy.size)
            if valx.size > 1:
                suffix = ""
                if info.key == "suivi":
                    isuiv += 1
                    suffix = "_%d" % isuiv
                key = info.key + suffix
                data[key] = Data(x=valx, y=valy,
                                 key=key, title=info.title + suffix,
                                 xlabel=None, ylabel=None)

        return data


class AdaoDecoder(AbstractDecoder):
    """Decoder that extract the values from Adao analysis."""
    _names = re.compile("Input variables: (?P<names>.*)$", re.M)
    _values = re.compile("Input values: (?P<values>.*)$", re.M)

    @classmethod
    def decode(cls, text):
        """Decode the given text.

        Arguments:
            text (str): Text of the messages files.

        Return:
            dict(Data): Ordered dict holding the data extracted from the text.
        """
        # pragma pylint: disable=eval-used
        data = OrderedDict()
        mat = cls._names.search(text)
        if not mat:
            return data

        found = list(cls._values.finditer(text))
        if not found:
            return data

        variables = eval(mat.group("names"))
        var_nb = len(variables)
        values = []
        for mat in found:
            val_i = eval(mat.group("values"))
            if len(val_i) != var_nb:
                continue
            values.append(val_i)
        values = numpy.array(values)
        absc = numpy.arange(len(values))

        for i, name in enumerate(variables):
            data[name] = Data(name, absc, values[:, i], name, None, None)

        return data


class Decoder(AbstractDecoder):
    """The meta-decoder that cumulates several decoders."""

    SubDecoders = (NLTimeDecoder, DynaVibraTimeDecoder, DynaVibraFreqDecoder,
                   ConvergenceDecoder, AdaoDecoder)

    @classmethod
    def decode(cls, text):
        """Decode the given text.

        Arguments:
            text (str): Text of the messages files.

        Return:
            dict(Data): Ordered dict holding the data extracted from the text.
        """
        data = OrderedDict()
        if text:
            text = remove_mpi_prefix(to_unicode(text))
            for class_ in cls.SubDecoders:
                try:
                    data_i = class_.decode(text)
                except Exception: # pylint: disable=broad-except
                    continue
                data.update(data_i)

        return data
