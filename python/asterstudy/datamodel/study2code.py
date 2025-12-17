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
Study2Code
----------

Dumps AsterStudy Stage internal representation into corresponding API calls.

"""


# The pragma below has to be removed after migration to Python 3 and
# suppression of above two lines.
# pragma pylint: disable=wrong-import-position,wrong-import-order

import re
from io import StringIO

from ..common import format_code
from .aster_parser import clean_expression
from .command import CO, Command
from .visit_study import obj_end, obj_start


class ExportToCodeVisitor:
    """Visitor of a DataSet to be dumped in terms if Command API.

    Args:
        stage_name (str): Name of the Stage object.
        ostream (output stream): File-like object on which write the text.
    """

    def __init__(self, stage_name, ostream):
        self.stage_name = stage_name
        self._write = ostream.write
        self.varstack = []
        self._vars = []

    def visit_dataset(self, dataset):
        """Visit a DataSet."""
        last = None
        for command in dataset:
            self._write('\n')
            if last == "_CONVERT_COMMENT":
                self._write("previous = command")
                self._write('\n')

            command.accept(self)

            if last == "_CONVERT_COMMENT":
                fmt = "{stage}.add_dependency(command, previous)"
                self._write(fmt.format(stage=self.stage_name))
                self._write('\n')
            last = command.title

        self._write("{stage}.reorder()".format(stage=self.stage_name))
        self._write('\n')

    def visit_stage(self, stage):
        """Visit a Stage."""
        stage.dataset.accept(self)

    def visit_command(self, command):
        """Visit a generic Command."""
        var = 'command'
        args = {'command':command,
                'stage': self.stage_name,
                'var': var}
        fmt = "{stage}({command.title!r})"
        if command.name != '_':
            fmt = "{stage}({command.title!r}, {command.name!r})"

        if command.keys():
            fmt = "{var} = " + fmt

        self._write(fmt.format(**args))
        self._write('\n')

        if command.keys():
            self.varstack.append(var)
            self._visit_keysmixing_based(command)
            self.varstack.pop(-1)

    visit_formula = visit_command

    def visit_variable(self, command):
        """Visit a Python variable"""
        self.visit_command(command)
        expr = clean_expression(command['EXPR'].value)

        deps = [i for i in self._vars if re.search(r'\b{}\b'.format(i), expr)]
        for varname in deps:
            fmt = "{stage}.add_dependency(command, {stage}['{var}'])"
            self._write(fmt.format(stage=self.stage_name, var=varname))
            self._write('\n')
        self._vars.append(command.name)

        self._write("command.update(expression={!r})".format(expr))
        self._write('\n')

    def visit_hidden(self, command):
        """Visit a Hidden."""
        # TODO: not empty!

    def visit_comment(self, comment):
        """Visit a Comment."""
        self.visit_command(comment)

    def visit_sequence(self, sequence):
        """Visit a Sequence of keywords."""
        var = 'sequence'
        name = sequence.name
        self._write('\n')
        self._write("%s = %s['%s']\n" % (var, self.varstack[-1], name))

        self.varstack.append(var)
        var = 'item'
        for item in sequence:
            self._write('\n')
            self._write("%s = %s.append()\n" % (var, self.varstack[-1]))
            self.varstack.append(var)
            self._visit_keysmixing_based(item)
            self.varstack.pop(-1)
        self.varstack.pop(-1)

        self._write('\n')

    def visit_factor(self, factor):
        """Visit a Factor keyword."""
        var = 'factor'
        name = factor.name
        self._write('\n')
        self._write("%s = %s['%s']\n" % (var, self.varstack[-1], name))
        self.varstack.append(var)
        self._visit_keysmixing_based(factor)
        self.varstack.pop(-1)
        self._write('\n')

    def visit_simple(self, simple):
        """Visit a Simple keyword."""
        name = simple.name
        self._write("%s['%s'] = " % (self.varstack[-1], name))
        self._export_value(simple.value)
        self._write('\n')

    def _export_value(self, value):
        """Export the value of a Simple keyword."""
        if isinstance(value, str):
            self._write(u"%s" % repr(value))
        elif isinstance(value, Command):
            self._write("%s['%s':command]" % (self.stage_name, value.name,))
        elif isinstance(value, CO):
            self._write(u"%s" % repr(value.name))
        elif isinstance(value, (list, tuple)):
            self._write(obj_start(value))

            for idx, item in enumerate(value):
                self._export_value(item)
                self._print_delimiter(idx, value)

            self._write(obj_end(value))
        else:
            self._write(str(value))

    def _visit_keysmixing_based(self, item):
        """Visit an object based on a KeysMixing."""
        keys = sorted(item.keys())
        for key in keys:
            item[key].accept(self)

    def _print_delimiter(self, idx, sequence):
        if idx != len(sequence) - 1:
            self._write(", ")


def study2code(dataset, stage_name='stage'):
    """Dumps Aster-Study DataSet in terms of its Command API"""
    ostream = StringIO()
    export = ExportToCodeVisitor(stage_name, ostream)

    dataset.reorder()
    dataset.accept(export)

    return format_code(ostream.getvalue())
