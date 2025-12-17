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
Comm2Study
----------

Implementation of the features to import code_aster syntax into the data model.

"""


import copy
import os
import os.path as osp
import sys
import traceback
from collections import OrderedDict

from ..common import (debug_message, debug_mode, format_code, mixedcopy,
                      no_new_attributes, old_complex, recursive_items,
                      split_text, to_unicode, translate)
from ..common.conversion import MARK, ConversionReport
from ..common.exceptions import ConversionError, IncludeConversion
from .abstract_data_model import add_parent
from .aster_parser import (change_text, comment_include, include_keyword,
                           remove_include)
from .aster_syntax import is_unit_valid
from .catalogs import CATA
from .command import CO as _CO
from .command import Variable
from .general import ConversionLevel

class Toggler:
    """Decorator that toggles commands activation/deactivation"""

    def __init__(self):
        self._active = True
        self._before = {}

    @property
    def active(self):
        """Attribute that holds the current state."""
        return self._active

    def enable(self, ctxt):
        """Enable the toggle."""
        unknown = object()
        self._active = True
        # restore previously existing objects that have not been commented
        for i, obj in ctxt.items():
            previous = self._before.get(i, unknown)
            if previous is not unknown and obj is not previous:
                ctxt[i] = previous

    def disable(self, ctxt):
        """Disable the toggle."""
        self._active = False
        self._before = ctxt.copy()


class CommandBuilder:
    """Builder of objects of AsterStudy data model.

    Use the current version of the code_aster commands catalog.

    Args:
        stage (Stage): The :obj:`datamodel.stage.Stage` object
            to fill.
        strict (ConversionLevel): Tells how strict the conversion must be.
                Default is not to fail.

    Attributes:
        _stg (Stage): The :obj:`datamodel.stage.Stage` object to fill.
        _strict (ConversionLevel): The level of conversion required.
        _cmd_results (dict): Stores the result returned by a command.
        _results_cmd (dict): Stores the command that returns a result.
        _saved (dict): Used to store temporary objects.
        _exec_ctxt (dict): Context of the command file.
        _vars (dict): Used to store value of Python variables.
        _reuse (dict): Store command reused by another.
        _del (dict): Store deleted commands.
        _unfinish (Command): Command currently added.
        _report (ConversionReport): Report object.
    """
    _stg = _unfinish = _strict = _cmd_results = _results_cmd = _saved = None
    _exec_ctxt = _vars = _reuse = _del = _toggle = _report = None
    __setattr__ = no_new_attributes(object.__setattr__)

    def __init__(self, stage, report, strict=ConversionLevel.NoFail):
        if not stage.is_graphical_mode():
            raise TypeError("The stage must be in graphical mode.")
        self._stg = stage
        self._report = report
        self._unfinish = None
        self._strict = strict
        self._cmd_results = {}
        self._results_cmd = {}
        self._saved = {}
        self._exec_ctxt = {}
        self._vars = {}
        self._reuse = {}
        self._del = OrderedDict()
        self._toggle = None
        CATA.command.register_call_callback(self._exec_command) 
        CATA.baseds.register_deepcopy_callback(self._deepcopy_ds)
        # methodeDef = CATA.get_command_definition('LIRE_MAILLAGE')
        # print(methodeDef)
        # print(CATA.get_main_categories_summary())

    @staticmethod
    def reset_callbacks():
        """Reset callbacks."""
        CATA.command.register_call_callback(None)
        CATA.baseds.register_deepcopy_callback(None)
    
    def _exec_command(self, ascommand, **kwargs):
        """Execution of the *ascommand*."""
        debug_message("executing aster command", ascommand.name)
        parents = []
        if not self._stg.is_empty():
            last = self._stg.dataset.get_last_command()
            if last.title == "_CONVERT_COMMENT":
                if ascommand.name == "_CONVERT_COMMENT":
                    # append the text of the comment to the previous comment
                    # debug_message("append to last comment", kwargs)
                    last["EXPR"] = last["EXPR"].value + "\n" + kwargs["EXPR"]
                    return None
                # add a dependency to the previous comment
                parents.append(last)

        kwargs = ignore_formula_args(ascommand, kwargs)
        kwargs = add_reuse_badcommands(ascommand, kwargs)
        kwargs = add_unit_default_value(ascommand, kwargs)
        kwargs = remove_identifier(kwargs)
        kwargs = nominal_value(ascommand, kwargs)
        kwargs = use_hidden_keywords(self._report, ascommand, kwargs)
        warn_on_inclmat(self._report, ascommand, kwargs)
        if self._stg.model.support["compat_syntax"]:
            compat = ascommand.get_compat_syntax()
            compat(kwargs)
            # debug_message("Compatibility returned:", ikwargs)
        # not to add default values
        tmp = mixedcopy(kwargs)
        # on éxecute la méthode ici.
        result = ascommand.call_default(__strict__=self._strict, **tmp)
        # debug_message("creating Command for", ascommand.name)
        command = self.add_command(ascommand.name, **kwargs)
        # store the result produced by the Command.
        if result is not None:
            self._cmd_results[command] = result
            self._results_cmd[result] = command
            debug_message("result stored for", command.title, result)

        # DETRUIRE
        if command.is_deleter:
            for cmd in command.deletes():
                self._del[cmd] = command

        command.active = self._toggle.active

        # if a macro-command produces additional results
        for hidden in command.hidden:
            hidden.check(safe=False)
            self._exec_ctxt[hidden.name] = hidden

        # In case of "reuse", a command result may be reset by the current
        # command, that's why we must name it now and not wait
        # for `_post_conversion()`.
        # Name previously created objects
        _locals = self._exec_ctxt
        for name, item in _locals.items():
            if not isinstance(item, CATA.baseds):
                continue

            cmd = self._results_cmd[item]
            cmd.name = name
            # debug_message("name updated", name, "for", cmd.title, item)

        for i in parents:
            # debug_message("adding parent of", command.title, ":", i.uid)
            add_parent(command, i)

        return result

    def _deepcopy_ds(self, datastructure, memodict=None):
        # pragma pylint: disable=unused-argument
        """Overrides the original *__deepcopy__* hook of *DataStructure*."""
        return self._results_cmd[datastructure]

    def add_command(self, title, **kwargs):
        """Add the new *Command* in the *Stage*."""
        cmd = self._stg.add_command(title, '_')
        self._unfinish = cmd
        ikwargs = copy.deepcopy(kwargs)
        if 'reuse' in ikwargs:
            self._reuse[cmd] = ikwargs['reuse']
            del ikwargs['reuse']
        ikwargs = convert_value(ikwargs)
        cmd.init(ikwargs, conversion=True)
        self._unfinish = None
        return cmd

    def _setup(self):
        """Build and setup the context to evaluate the commands file.

        Returns:
            dict: Context to execute the commands file.
        """
        vartype = CATA.package("DataStructure").PythonVariable
        context = {}

        # Update context with commands from preceding stages
        for stage in self._stg.preceding_stages:
            for command in stage:
                if command.name in ['', '_']:
                    continue

                # Create an instance of the result type
                result_type = command.gettype(self._strict)

                if isinstance(command, Variable):
                    result = vartype()
                else:
                    result = result_type()

                try:
                    self._results_cmd[result] = command
                except TypeError: # pragma: no cover
                    # ignore list, dict results
                    pass
                context[command.name] = result

        # add code_aster command dictionary
        context.update(CATA.iteritems())

        self._toggle = Toggler()
        context['_DISABLE_COMMANDS'] = self._toggle.disable
        context['_ENABLE_COMMANDS'] = self._toggle.enable

        # support of CO object
        context['CO'] = _CO

        # add basic mathematical functions
        context.update(Variable.initial_context())

        context['IncludeConversion'] = IncludeConversion

        # We could generate the function name to avoid possible conflict
        context["_post_conversion"] = self._post_conversion
        # change output streams
        if not debug_mode():
            self._saved['sys.stdout'] = sys.stdout
            sys.stdout = open(os.devnull, "w")
            self._saved['sys.stderr'] = sys.stderr
            sys.stderr = open(os.devnull, "w")

        return context

    def _teardown(self):
        """Restore initial state."""
        if not debug_mode():
            if hasattr(sys.stdout, 'close'):
                sys.stdout.close()
            if hasattr(sys.stderr, 'close'):
                sys.stderr.close()
            sys.stdout = self._saved['sys.stdout']
            sys.stderr = self._saved['sys.stderr']

    def _post_conversion(self):
        """Post-conversion function to name the results in *Command* objects.

        Arguments:
            _locals (dict): Context of the comm file.
        """
        _locals = self._exec_ctxt
        _unauthorized = list(CATA)
        # store the name of code_aster datastructures
        result_names = {}
        for name, result in _locals.items():
            if isinstance(result, CATA.baseds):
                if name in _unauthorized:
                    raise ValueError("Unauthorized name: {0!r}".format(name))
                result_names[result] = name
                # debug_message("naming result", result, "as", name)
        # store results names in Command objects and evaluate user variables
        results = result_names.keys()
        # it is important to loop on commands by creation order for DETRUIRE
        deleters = OrderedDict()
        for cmd in self._stg:
            if cmd in self._del:
                deleters[cmd] = self._del[cmd]
            _check_deleters(cmd, deleters)

            result = self._cmd_results.get(cmd)
            if result is None:
                continue

            if result in results:
                cmd.name = result_names[result]
                # debug_message("naming result of", cmd.title, ":", cmd.name)
            elif cmd in self._reuse:
                # because of tolerated syntax "cmd(reuse='xx', ...)"
                if cmd.name == '_':
                    warn_on_reuse_syntax(self._report, cmd)
                cmd.name = self._reuse[cmd].name
                # debug_message("reuse name for", cmd.title, ":", cmd.name)
            if self._strict & ConversionLevel.Naming and \
                    cmd.name in ('', '_'):
                raise NotImplementedError("can not name command: {0}"
                                          .format(cmd))

    def convert(self, intext):
        """Fill the stage from a commands file (given as text).

        Arguments:
            intext (str): Content of the commands file.

        Returns:
            str: The remaining text that hasn't been converted if the *strict*
            attribute contains *Partial*. Otherwise, this remaining text is
            added to a text stage.
        """
        init_size = len(self._stg)
        intext = to_unicode(intext)
        eoi, text = change_text(intext, self._strict, self._report)

        text = "{0}\n_post_conversion() # {1}\n".format(text, MARK)
        self._exec_ctxt = self._setup()
        remaining = ""
        try:
            exec(text, self._exec_ctxt) # pragma pylint: disable=exec-used
        except Exception as exc: # pragma pylint: disable=broad-except
            self._teardown()
            details = traceback.format_exc()
            eoprev, lineno, line = _locate_error(exc, eoi, text)
            if (self._strict & ConversionLevel.Partial or
                    isinstance(exc, IncludeConversion)):
                debug_message("Conversion failed, split after line", eoprev)
                # remove the unfinished command
                if self._unfinish:
                    del self._stg[self._unfinish]
                # _post_conversion was not called
                try:
                    self._post_conversion()
                except Exception: # pragma pylint: disable=broad-except
                    # some commands have not be named...
                    pass
                part1, astext = split_text(intext, eoprev, remove=MARK)
                # debug_message("+" * 50)
                # debug_message(part1)
                # debug_message("-" * 50)
                # debug_message(astext)
                # debug_message("=" * 50)
                # in case of SyntaxError, nothing has been added
                if isinstance(exc, SyntaxError):
                    debug_message("SyntaxError: convert first part separately")
                    remaining = _comm2study(part1, self._stg, self._report,
                                            self._strict)
                if astext:
                    remaining += os.linesep + comment_include(astext)
            else:
                # revert the input stage as it was
                while len(self._stg) > init_size:
                    del self._stg[-1]
                # message for CheckerError (didn't exist in older versions)
                if hasattr(exc, 'msg'):
                    exc = exc.msg # pragma pylint: disable=no-member
                raise ConversionError(exc, details, lineno, line) from None
        else:
            self._teardown()
        return remaining


def _locate_error(exc, eoi, text):
    """Return the line number and the line where the exception occurred.

    Returns:
        int: Line number of the end of the previous (successfull) instruction.
        int: Line number of the error.
        line: Line content where the error occurred.
    """
    if isinstance(exc, SyntaxError):
        lineno = exc.args[1][1]
        line = (exc.args[1][3] or "").strip()
    else:
        # 0: here, 1: executed text
        ltb = traceback.extract_tb(sys.exc_info()[-1], limit=3)
        try:
            tbck = ltb[1]
            lineno = tbck[1]
        except IndexError: # pragma: no cover
            lineno = -1

    debug_message("Error at line", lineno, "end of instr", eoi)
    debug_message(exc)
    lines = text.splitlines()
    upto = []
    offset = 0
    for i in eoi:
        if i >= lineno:
            break
        orig = i - offset
        if lines[i - 1].startswith("raise NotImplementedError"):
            offset += 1
        else:
            upto.append(orig)

    eoprev = upto.pop(-1) if upto else 0
    debug_message("Previous instr at line", eoprev, "(original text)")

    if not isinstance(exc, SyntaxError):
        line = lines[lineno - 1] if len(lines) > lineno - 2 else "?"

    return eoprev, lineno, line


def _check_deleters(command, deleters):
    """Check if a Command reuse a name of a previously deleted result.
    In this case, the Command must depend on the deleter.

    Arguments:
        command (Command): Command currently checked.
        deleters (dict): Dict `{deleted: deleter}`.
    """
    delnames = [i.name for i in deleters.keys()]
    name = command.name
    if name in ('', '_'):
        return

    if name in delnames:
        # add a dependency to DETRUIRE of the previous 'name'
        delcmds = [(i, val) for i, val in deleters.items() \
                       if i.name == name and i != command]
        if not delcmds:
            return
        key, deleter = delcmds[0]
        del deleters[key]
        debug_message("add deps {0.title}<{0.uid}> vers {1.title}<{1.uid}>"
                      .format(command, deleter))
        add_parent(command, deleter)


class SetKeywordValue:
    """Visitor of a catalog of command to set value of some keywords.

    Attributes:
        _checker (function): Predicate used to select filter keywords.
        _setter (function): Function that returns the new value for a simple
            keyword.
        _values (dict): Dict of user keywords.
        _parent (str): Name of the current factor keyword or None at the top
            level.
        _current (str): Name of the keyword currently analysed.
    """

    def __init__(self, checker, setter, userdict):
        self._checker = checker
        self._setter = setter
        self._values = userdict
        self._parent = None
        self._current = None

    def _visit_composite(self, compo, eval_dict):
        """Visit a composite object (command, factor keywords...)"""
        compo.addDefaultKeywords(eval_dict)
        for key, kwd in compo.definition.iterItemsByType():
            self._current = key
            kwd.accept(self, eval_dict)
            self._current = None

    def visit_simple(self, simple, _):
        """Visit a simple keyword."""
        if self._checker(simple):
            store = self._values
            if self._parent is not None:
                values = self._values
                store = values[self._parent] = values.get(self._parent, {})

            value = self._setter(simple)
            if isinstance(store, dict):
                store = [store, ]
            for occ in store:
                self._set(occ, value)

    def _set(self, store, value):
        """Set the value in dict"""
        if self._current not in store:
            # debug_message("Add default value: {0}={1!r}".format(
                # self._current, value))
            store[self._current] = value

    def visit_factor(self, factor, eval_dict):
        """Visit a factor keyword."""
        if self._current not in self._values:
            return
        self._parent = self._current
        self._visit_composite(factor, eval_dict)
        self._parent = None

    def visit_bloc(self, bloc, eval_dict):
        """Visit a block: does nothing because condition is not evaluated."""
        if bloc.isEnabled(eval_dict):
            self._visit_composite(bloc, eval_dict)

    visitCommand = _visit_composite
    visitMacro = _visit_composite
    visitFactorKeyword = visit_factor
    visitSimpleKeyword = visit_simple
    visitBloc = visit_bloc


def add_unit_default_value(command, kwargs):
    """Set the value of UNITE keywords that have no value to default."""
    unittype = CATA.package("DataStructure").UnitBaseType

    def _predicate(simple):
        if simple.definition.get('defaut') is None:
            return False
        if not is_unit_valid(simple.definition['defaut']):
            return False
        typ = simple.definition['typ']
        try:
            return issubclass(typ, unittype)
        except TypeError:
            pass
        return False

    def _setter(simple):
        return simple.definition.get('defaut')

    visitor = SetKeywordValue(_predicate, _setter, kwargs)
    utils = CATA.package("SyntaxUtils")
    eval_dict = utils.mixedcopy(kwargs)
    command.accept(visitor, eval_dict)
    return kwargs


def add_reuse_badcommands(ascommand, kwargs):
    """Set the value of keywords to handle properly reuse property for
    uncorrect command."""
    # MECA_STATIQUE
    if ascommand.name == "MECA_STATIQUE":
        if 'reuse' in kwargs and 'RESULTAT' not in kwargs:
            kwargs["RESULTAT"] = kwargs['reuse']
    # MACR_ELEM_STAT
    elif ascommand.name == "MACR_ELEM_STAT":
        if 'reuse' in kwargs and 'MACR_ELEM' not in kwargs:
            kwargs["MACR_ELEM"] = kwargs['reuse']
    # MACRO_ELAS_MULT
    elif ascommand.name == "MACRO_ELAS_MULT":
        if 'reuse' in kwargs and 'RESULTAT' not in kwargs:
            kwargs["RESULTAT"] = kwargs['reuse']
    # DEFI_DOMAINE_REDUIT
    elif ascommand.name == "DEFI_DOMAINE_REDUIT":
        if 'reuse' in kwargs and 'MAILLAGE' not in kwargs:
            kwargs["MAILLAGE"] = kwargs['reuse']
    # CREA_RESU
    elif ascommand.name == "CREA_RESU":
        if 'reuse' in kwargs and kwargs.get("OPERATION") == "AFFE":
            kwargs["RESULTAT"] = kwargs['reuse']
    return kwargs


def ignore_formula_args(ascommand, kwargs):
    """Remove additional arguments used to pass external objects to a formula.
    """
    if ascommand.name != "FORMULE":
        return kwargs
    for key in list(kwargs.keys()):
        if key not in ('NOM_PARA', 'VALE', 'VALE_C'):
            del kwargs[key]
    return kwargs


def remove_identifier(kwargs):
    """Remove 'identifier' mark."""
    if 'identifier' in kwargs:
        del kwargs['identifier']
    return kwargs


def nominal_value(command, kwargs):
    """Keep only nominal value of '_CONVERT_VARIABLE'."""
    if command.name == "_CONVERT_VARIABLE" and "EXPR" in kwargs:
        if kwargs["EXPR"].strip().startswith("VARIABLE"):
            # pragma pylint: disable=eval-used,invalid-name,unused-argument
            def _expr(NOM_PARA=None, VALE=None):
                return VALE
            ctxt = dict(VARIABLE=_expr)
            kwargs = {'EXPR': repr(eval(kwargs["EXPR"], ctxt))}
    return kwargs


def use_hidden_keywords(report, command, kwargs):
    """Reports a warning in case of hidden keywords in use."""
    # do not warn about these !§%#* commands
    if command.name in ("CALC_SPECTRE_IPM", "DYNA_ALEA_MODAL", "MACR_SPECTRE"):
        return kwargs

    found = False
    for key, _ in recursive_items(kwargs):
        keyword = key[0]
        if len(key) == 4:
            keyword = key[2]
        if keyword in ("MAILLE", "NOEUD"):
            found = True
            break
    if found:
        report.warn(translate("AsterStudy",
                              "The imported file contains NOEUD/MAILLE in {0} "
                              "which are now deprecated. You cannot change "
                              "their value. If you edit this command you will "
                              "need to select a group.").format(command.name))
    return kwargs


def convert_value(obj):
    """Convert old-style values"""
    # pragma pylint: disable=no-member
    obj = old_complex(obj)
    if isinstance(obj, dict):
        for key, value in obj.items():
            obj[key] = convert_value(value)
    elif isinstance(obj, list):
        for i, j in enumerate(obj):
            obj[i] = convert_value(j)
    elif isinstance(obj, tuple):
        obj = tuple(convert_value(i) for i in obj)
    return obj


def _comm2study(content, stage, report, strict):
    """Conversion function wrapped by :func:`comm2study`.

    Arguments:
        See :func:`comm2study`.
    """
    nbs = stage.parent_case.nb_stages
    debug_message("starting new conversion of stage", stage.number, "/", nbs)
    assert not strict & ConversionLevel.Partial or stage.number == nbs
    builder = CommandBuilder(stage, report, strict)

    not_converted = ''
    try:
        not_converted = builder.convert(content)
        if stage.is_graphical_mode():
            stage.reorder()
    finally:
        builder.reset_callbacks()

    warn_on_reuse(report, stage)
    return not_converted

    
def comm2study(content, stage, strict=ConversionLevel.NoFail, provider=None,
               report=None, update=False):
    """Import a text of code_aster commands into the *Stage* object.

    Arguments:
        content (str|bytes): Text of code_aster commands to import.
        stage (Stage): *Stage* in which the *Command* objects are added.
        strict (ConversionLevel): Tells how strict the conversion must be.
            See `general.ConversionLevel` for more details.
            Default is not to fail.
        provider (*FileProvider*): Instance of *FileProvider* that can provide
            additional COMM files on demand.
        report (*ConversionReport*): Object that stores the conversion report.

    Returns:
        str: The remaining text that hasn't been converted if the *strict*
        attribute contains *Partial*. Otherwise, this remaining text is
        added to a text stage.
    """
    if update:
        return update_stage(content, stage, strict, provider, report)
    report = report or ConversionReport()
    case = stage.parent_case
    existing = [i.uid for i in case]
    previous = "?"
    try:
        while content:
            assert to_unicode(content) != previous, "infinite loop detected"
            first = stage
            content = _comm2study(content, stage, report, strict)
            if not content:
                break

            # support of INCLUDE
            content, tag = remove_include(content)
            if tag:
                debug_message("INCLUDE detected with tag", tag)
                if not provider.is_available(tag):
                    content = ("INCLUDE({0})\n".format(include_keyword(tag))
                               + content)
                    raise ConversionError(KeyError(tag), "", 0, "INCLUDE")

                debug_message("Converting INCLUDE content...")
                name = osp.splitext(osp.basename(provider.filename(tag)))[0]
                stage = _create_or_rename(case, name)
                include = provider.content(tag)
                comm2study(include, stage, strict, provider)

                debug_message("Post-INCLUDE conversion...")
                stage = _create_or_rename(case, first.name)
                content = comm2study(content, stage,
                                     strict | ConversionLevel.Partial, provider)
            else:
                # add the not converted part in a new text stage
                raise ConversionError

            previous = content

    except Exception as exc: # pragma pylint: disable=broad-except
        if not strict & ConversionLevel.Partial:
            # in case of error, clean additional created stages
            # but commands may have be added to 'first'
            for added in reversed([i for i in case if i.uid not in existing]):
                del case[added]
            report.error(exc)
            raise

        # in case of failure with a provider or Partial, store as text stage
        debug_message("Put remaining text in text mode")
        stage = _create_or_rename(case, stage.name)
        try:
            content = format_code(content)
        except SyntaxError:
            pass
        stage.use_text_mode()
        stage.set_text(content)
        content = ""

    return content


def update_stage(content, stage, strict=ConversionLevel.NoFail, provider=None,
               report=None):
    report = report or ConversionReport()
    case = stage.parent_case
    existing = [i.uid for i in case]
    previous = "?"
    try:
        while content:
            assert to_unicode(content) != previous, "infinite loop detected"
            first = stage
            content = _comm2study(content, stage, report, strict)
            print(stage, "après update :")            
            if not content:
                break
    except Exception as exc: # pragma pylint: disable=broad-except
        if not strict & ConversionLevel.Partial:
            # in case of error, clean additional created stages
            # but commands may have be added to 'first'
            for added in reversed([i for i in case if i.uid not in existing]):
                del case[added]
            report.error(exc)
            raise

        # in case of failure with a provider or Partial, store as text stage
        debug_message("Put remaining text in text mode")
        stage = _create_or_rename(case, stage.name)
        try:
            content = format_code(content)
        except SyntaxError:
            pass
        stage.use_text_mode()
        stage.set_text(content)
        content = ""

    return content

def _create_or_rename(case, name):
    """Reuse the last stage if it is empty or create a new one."""
    stage = case[-1]
    if stage.is_empty():
        stage.use_graphical_mode()
    else:
        stage = case.create_stage(name)
    return stage


def warn_on_reuse(report, stage):
    """Warn about usage of 'reuse'.

    Arguments:
        report (*ConversionReport*): Report object.
        stage (*Stage*): Newly created stage.
    """
    # names['result'] = [cmd1, cmd2... that uses a result with this name]
    names = {}
    for cmd in stage.sorted_commands:
        if cmd.name:
            if cmd.need_reuse():
                # commands that use a previous object with the same name
                # except commands that modify the object
                use_name = {i for i in names.get(cmd.name, [])
                            if i.name != cmd.name}
                # use_name = set(names.get(cmd.name, []))
                # ignore commands that are using the current one
                use_prev = use_name.difference(cmd.child_commands)
                if use_prev:
                    msg = translate("AsterStudy",
                                    "The object '{0.name}' is changed "
                                    "by {0.title}.\n"
                                    "The following commands are using a  "
                                    "previous instance of '{0.name}':\n{1}\n\n"
                                    "Type 'Ctrl+<F>' to search '{0.name}' and "
                                    "check that these commands are "
                                    "using the right instance of this object.")
                    cmds = "\n".join([_format_cmd(i) for i in use_prev])
                    report.warn(msg.format(cmd, cmds))
            for parent in cmd.parent_commands:
                names.setdefault(parent.name, [])
                names[parent.name].append(cmd)


def warn_on_reuse_syntax(report, command):
    """Warn about commands with 'reuse' that do not name the new result.

    Arguments:
        report (*ConversionReport*): Report object.
        command (*Command*): Newly created command.
    """
    msg = translate("AsterStudy",
                    "`{0.title}(reuse={0.name}, ...)` without setting the "
                    "result object is tolerated and should work in most "
                    "cases.\n\n"
                    "Type 'Ctrl+<F>' to search '{0.name}' and "
                    "check the reused object is used.")
    report.warn(msg.format(command))


def warn_on_inclmat(report, command, kwargs):
    """Warn about unsupported INCLUDE_MATERIAU/FICHIER.

    Arguments:
        report (*ConversionReport*): Report object.
        command (*code_aster.Command*): Newly created code_aster command.
        kwargs (*dict*): Command arguments.
    """
    if command.name == 'INCLUDE_MATERIAU' and kwargs.get('FICHIER'):
        msg = translate("AsterStudy",
                        "`{0.name}(FICHIER=...)` is not supported.\n"
                        "Workaround: insert a stage above in text mode and "
                        "add an input file selecting '{1}'.\n\n"
                        "Then type 'Ctrl+<F>' to search '{1}' and enter "
                        "FICHIER='fort.N' (with the used number).")
        report.warn(msg.format(command, kwargs['FICHIER']))


def _format_cmd(cmd):
    return "{0.title} ({0.name})".format(cmd) if cmd.name != '_' else cmd.title
