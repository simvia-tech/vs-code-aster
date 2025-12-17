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
Study2Comm
----------

AsterStudy Stage Converter to code_aster COMM file format.

"""


import os
import re
from functools import wraps

from ..common import Features, no_new_attributes, translate
from ..common.conversion import COMMENT
from .command import CO, Command, Comment
from .visit_study import obj_end, obj_start


def with_active(meth):
    """Decorator on a method to enable/disable the 'active' state according
    to the command 'active' state.
    Arguments:
        meth: Method to wrap that accepts a Command as first argument.
    """
    @wraps(meth)
    def wrapper(self, command, *args, **kwds):
        """Wrapper of a method taking a `command` as first argument."""
        orig = self.active
        try:
            self.active = command.active
            result = meth(self, command, *args, **kwds)
        finally:
            self.active = orig

        return result
    return wrapper


class ExportToCommVisitor:
    """Visitor of a DataSet to be exported as a code_aster comm file.

    Arguments:
        support (Features): Supported features object.
        sort (bool): By default commands are sorted according to their
            dependencies. For unittests and keep order for commands without
            dependencies, one may use *False*.
        limit (int): Limits the output to the first occurrences of factor
            keywords or in the lists of values. Warning: Using *limit* may
            generate an invalid commands file.
        add_ids (bool): Add 'identifier' of Commands.
        format_id (str): Format used for the command identifier.
        indent (int): Initial indentation.
        rename (bool): Export command with a generated name (used for
            *copy/paste*).
    """
    interrupt_value = '"_interrupt_MARK_value_"'
    interrupt_fact = '_interrupt_MARK_fact_()'

    _sort = _limit = _limit_reached = _ids = _formula_deps = None
    _idx = _id_format = _rename = None
    active = lines = curline = indent = None
    __setattr__ = no_new_attributes(object.__setattr__)

    @classmethod
    def factory(cls, support, pretty, parametric, **opts):
        """Factory that choose the proper Export class.

        Arguments:
            support (Features): Supported features object.
            pretty (bool): If *True* the output preserve alignment. Otherwise
                the text is more compact, with less spaces.
            parametric (bool): If *True* the Python variable are wrapped by
                a function call.
            opts (keyword arguments): See constructor.
        """
        if parametric:
            class_ = ExportToCommParamVisitor
        elif pretty:
            class_ = ExportToCommVisitor
        else:
            class_ = ExportToRawVisitor
        return class_(support, **opts)

    def __init__(self, support, sort=True, limit=0, add_ids=False,
                 format_id="{id}", indent=0, rename=False):
        support = support or Features()
        self._sort = sort
        self._limit = limit
        self._ids = support["command_ids"] and add_ids
        self._formula_deps = support["formula_deps"]
        self._idx = -1
        self._id_format = format_id
        self._limit_reached = False
        self._rename = rename
        self.active = True

        self.lines = []
        self.curline = []
        self.indent = [indent, ]

    def _write(self, text):
        self.curline.append(text)

    def _newline(self):
        """Initialize a new line."""
        if not self.active:
            self.curline.insert(0, COMMENT)
        self._endline()
        self.curline.append(" " * self.indent[-1])

    def _endline(self):
        """Add the current line."""
        line = ''.join(self.curline)
        if line.strip() != '':
            self.lines.append(line)
        self.curline = []

    def _add_indent(self):
        """Set the next indent spacing."""
        self.indent.append(len(''.join(self.curline)))

    def _reset_indent(self):
        """Revert indent spacing to its previous level."""
        self.indent.pop(-1)

    def get_text(self):
        """Return the text"""
        return os.linesep.join(self.lines)


    def visit_stage(self, stage):
        """Visit a Stage."""
        stage.dataset.accept(self)

    def visit_dataset(self, dataset):
        """Visit a DataSet."""
        if self._sort:
            cmds = dataset.sorted_commands
        else:
            cmds = dataset.commands
        # move DEBUT/POURSUITE and their comments first
        loop = []
        while cmds:
            cmd = cmds.pop(0)
            if not isinstance(cmd, Comment):
                cmds.insert(0, cmd)
                break
            loop.append(cmd)
        loop.extend([cmd for cmd in cmds if cmd.is_prologue])
        loop.extend([cmd for cmd in cmds if not cmd.is_prologue])
        for command in loop:
            self._idx += 1
            command.accept(self)

    @with_active
    def visit_command(self, command, storage=None):
        """Visit a generic Command."""
        if self._rename:
            case = command.stage.parent_case
            name = case.generate_name(command, check_previous=True)
        else:
            name = command.name
        if name != "_":
            self._write(self.decorate_name(name))
            self._print_equal()
        self._write(self.decorate_title(command.title))
        self._print_left_brace()
        self._add_indent()
        self._print_ids()
        # if limit is set, do not check if reuse is required
        if self._limit <= 0 and command.need_reuse():
            self._write(self.decorate_keyword("reuse"))
            self._print_equal(with_spaces=False)
            self._write(self.decorate_name(name))
            self._print_delimiter(0, (None, None), with_eol=True)
        self._visit_keysmixing_based(storage or command.storage_nocopy)
        self._print_right_brace()
        self._reset_indent()
        self._print_eol()
        self.lines.append("")

    def visit_hidden(self, dummy):
        """Visit a Hidden."""

    def visit_formula(self, formula):
        """Visit a Formula."""
        # a light copy is sufficient
        storage_adds = formula.storage_nocopy.copy()
        if self._formula_deps:
            dataset = formula.stage.dataset
            deps = formula.external_deps
            for name in deps:
                try:
                    storage_adds[self._at_end(name)] = dataset[name]
                except StopIteration:
                    continue
        self.visit_command(formula, storage_adds)

    @with_active
    def visit_variable(self, var):
        """Visit a Variable."""
        self._write(self.decorate_name(var.name))
        self._print_equal()
        self._write(var['EXPR'].value)
        self._print_eol()
        self.lines.append("")

    def visit_comment(self, comment):
        """Visit a Comment."""
        lines = comment['EXPR'].value.splitlines()
        lines.insert(0, "")
        self._write(self.decorate_comment("\n# ".join(lines).lstrip()))
        self._print_eol()

    def _visit_sequence(self, name, sequence):
        self._write(self.decorate_keyword(name))
        self._print_equal(False)
        if len(sequence) > 1:
            self._print_left_brace()

        self._add_indent()
        for idx, item in enumerate(sequence):
            self._write(self.decorate_special('_F'))
            self._print_left_brace()
            self._add_indent()
            self._visit_keysmixing_based(item)
            self._print_right_brace()
            self._reset_indent()
            if self._limited(idx, sequence, self.interrupt_fact):
                break
            self._print_delimiter(idx, sequence, with_eol=True)

        if len(sequence) > 1:
            self._print_right_brace()
        self._reset_indent()

    def _visit_simple(self, name, value):
        self._write(self.decorate_keyword(name))
        self._print_equal(False)
        if isinstance(value, str):
            self._write("{0!r}".format(value))
        elif isinstance(value, Command):
            self._write(self.decorate_name(value.name))
        elif isinstance(value, CO):
            self._write(self.decorate_special('CO'))
            self._print_left_brace()
            self._write(repr(self.decorate_name(value.name)))
            self._print_right_brace()
        elif isinstance(value, (list, tuple)):
            self._write(obj_start(value))

            for idx, item in enumerate(value):
                if isinstance(item, Command):
                    self._write(self.decorate_name(item.name))
                elif isinstance(item, str):
                    self._write("{0!r}".format(item))
                else:
                    self._write(repr(item))

                if self._limited(idx, value, self.interrupt_value):
                    break
                self._print_delimiter(idx, value)

            self._write(obj_end(value))
        else:
            self._write("%s" % (value,))

    def _visit_keysmixing_based(self, item):
        """Visit an object based on a KeysMixing."""
        keys = sorted(item.keys())
        for idx, key in enumerate(keys):
            obj = item[key]
            if obj is None:
                continue
            key = self._repl_end(key)
            self._visit_pyobj(key, obj)
            self._print_delimiter(idx, keys, with_eol=True)

    def _visit_pyobj(self, name, obj):
        """Replace real Visitor methods (needed to speed-up export)."""
        if isinstance(obj, (list, tuple)):
            if obj and isinstance(obj[0], dict):
                self._visit_sequence(name, obj)
            else:
                self._visit_simple(name, obj)
        elif isinstance(obj, dict):
            self._visit_sequence(name, [obj])
        else:
            self._visit_simple(name, obj)

    def _print_ids(self):
        if self._ids:
            self._write(self.decorate_name("identifier"))
            self._print_equal(with_spaces=False)
            self._write(repr(self._id_format.format(id=self._idx)))
            self._print_delimiter(1, [], with_eol=True)

    def _print_delimiter(self, idx, sequence, with_eol=False):
        if idx != len(sequence) - 1:
            if with_eol:
                self._write(",")
                self._print_eol()
            else:
                self._write(", ")

    def _print_eol(self):
        self._newline()

    def _print_equal(self, with_spaces=True):
        if with_spaces:
            self._write(' = ')
        else:
            self._write('=')

    def _print_left_brace(self):
        self._write('(')

    def _print_right_brace(self):
        self._write(')')

    def _limited(self, idx, sequence, string):
        """Tell if the output must be limited."""
        if (self._limit <= 0 or idx < self._limit - 1
                or idx == len(sequence) - 1):
            return False
        self._limit_reached = True
        self._print_delimiter(0, [])
        self._write(string)
        return True

    def end(self):
        """Close the export"""
        if self._limit_reached:
            self._write(self.decorate_comment(
                translate("AsterStudy",
                          "# sequences have been limited to the first "
                          "{} occurrences.").format(self._limit)))
            self._endline()

    @classmethod
    def clean(cls, text):
        """Clean a text generated by *ExportToCommVisitor*."""
        text = text.replace(cls.interrupt_value, "...")
        text = text.replace(cls.interrupt_fact, "...")
        return text

    def decorate_name(self, text): # pragma pylint: disable=no-self-use
        """Decorate item's name."""
        return text

    def decorate_title(self, text): # pragma pylint: disable=no-self-use
        """Decorate catalogue name."""
        return text

    def decorate_keyword(self, text): # pragma pylint: disable=no-self-use
        """Decorate keyword's name."""
        return text

    def decorate_comment(self, text): # pragma pylint: disable=no-self-use
        """Decorate comment."""
        return text

    def decorate_special(self, text): # pragma pylint: disable=no-self-use
        """Decorate special word."""
        return text

    @classmethod
    def _at_end(cls, key):
        """Return a modified key to be pushed at the end of the list of
        keywords."""
        return "~~~" + key

    _re_end = re.compile("^~~~")
    @classmethod
    def _repl_end(cls, key):
        """Return the original key from a key modified by `_at_end()`."""
        return cls._re_end.sub('', key)


class ExportToCommParamVisitor(ExportToCommVisitor):
    """Visitor of a DataSet to be exported as a code_aster comm file for
    parametric studies. Python variables are wrapped by a function that keeps
    its name and its nominal value.
    """

    def visit_variable(self, var):
        """Visit a Variable."""
        self._write(self.decorate_name(var.name))
        self._print_equal()
        self._write(self.decorate_title('VARIABLE'))
        self._print_left_brace()
        self._add_indent()

        self._visit_simple('NOM_PARA', var.name)
        self._print_delimiter(1, [], with_eol=False)

        self._write(self.decorate_keyword('VALE'))
        self._print_equal(False)
        self._write("%s" % (var['EXPR'].value, ))

        self._print_right_brace()
        self._reset_indent()
        self._print_eol()
        self.lines.append("")


class ExportToRawVisitor(ExportToCommVisitor):
    """Visitor of a DataSet to be exported as a code_aster comm file in
    a raw format.
    """

    def _newline(self):
        """Initialize a new line."""
        if not self.active:
            self.curline.insert(0, COMMENT)
        self._endline()

    def _endline(self):
        """Add the current line."""
        line = ''.join(self.curline)
        if line.strip() != '':
            self.lines.append(line)
        self.curline = []

    def _print_delimiter(self, idx, sequence, with_eol=False):
        if idx != len(sequence) - 1:
            self._write(", ")

    def get_text(self):
        return super().get_text().strip()


def study2comm(stage, support=None, pretty=True, parametric=False, **opts):
    """Exports AsterStudy Commands into code_aster COMM file format.

    By default the commands are sorted to respect their dependencies.
    Using ``sort=False`` may be required to keep the order of commands that
    have no dependencies. This is useful to have reproductible results in
    unittests.

    ``support`` provides the supported features of the destination version.
    If it is *None*, the *Features* object of the *History* that ``stage``
    belongs to is used if any, else a default object that supports all
    features will be created.

    Use ``limit=NN`` to limit the output to the fist ``NN`` occurrences in
    sequences.

    Use ``add_ids=True`` to add the *Command* ids in the commands file.

    Arguments:
        stage (Stage): Graphical Stage to be exported.
        support (Optional[Features]): Supported features object.
        pretty (Optional[bool]): Enable pretty formatting (Default: OFF).
        parametric (Optional[bool]): Export for a parametric study.
        opts (dict): Keywords arguments (see `ExportToCommVisitor`).

    Returns:
        str: Text of the COMM file.
    """
    support = support or (stage.model and stage.model.support or Features())
    assert support["parametric"] or not parametric, \
        "Selected version does not support parametric features."
    export = ExportToCommVisitor.factory(support, pretty, parametric, **opts)

    stage.accept(export)
    export.end()

    text = export.clean(export.get_text())
    return text


def _debug_write(writer): # pragma: no cover
    """Debug helper: also dump text on output"""
    import sys
    def _wrap(text):
        sys.stdout.write(text)
        writer(text)
    return _wrap
