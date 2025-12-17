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
Parser of COMM files
--------------------

Implementation of a mini parser to improve import of code_aster commands files.

"""


# The pragma below has to be removed after migration to Python 3 and
# suppression of above two lines.
# pragma pylint: disable=wrong-import-position,wrong-import-order

import ast
import os
import re
import token
import tokenize
from io import StringIO

from ..common import (AsterStudyError, ConversionError, debug_message,
                      debug_mode, to_unicode, translate)
from ..common.conversion import MARK, COMMENT
from ..common.utilities import format_expr
from .catalogs import CATA
from .general import ConversionLevel


def clean_expression(text):
    """Clean expression before evaluation.

    Arguments:
        text (str): expression to clean.

    Returns:
        str: cleaned expression without trailing semi-colon.
    """
    if not hasattr(clean_expression, "re_expr"):
        clean_expression.re_expr = re.compile("[; ]*$")
    return clean_expression.re_expr.sub("", text)


def _uncomment_commands(text):
    lines = text.splitlines()
    new = []
    active = True
    for line in lines:
        if line.startswith(COMMENT):
            if active:
                new.append("_DISABLE_COMMANDS(globals())")
            new.append(line.replace(COMMENT, ""))
            active = False
        else:
            if not active:
                new.append("_ENABLE_COMMANDS(globals())")
            active = True
            new.append(line)

    if new and new[-1]:
        new.append("")
    return os.linesep.join(new)


def _change_text(text):
    """Pre-processing of the input text.

    - Wrap constant parameters:

      ``a = 1`` is converted as ``a = _CONVERT_VARIABLE(EXPR="1")``

    - Wrap commented/inactive commands:

      ``#comment: mesh = LIRE_MAILLAGE()`` is converted as::

        _DISABLE_COMMANDS(globals())
        mesh = LIRE_MAILLAGE()
        _ENABLE_COMMANDS(globals())

    - Wrap comments:

      ``# line of comment.`` is converted as
      ``_CONVERT_COMMENT(EXPR="# line of comment.")``

    Returns:
        list[int]: list of line numbers of end of instruction.
        str: changed text.
    """
    text = _uncomment_commands(text)
    generator = tokenize.generate_tokens(StringIO(text).readline)
    result = []
    buff = []
    eoi = []
    started = False
    try:
        for ret in generator:
            num, val = ret[:2]
            started = started or num == token.NAME
            # _debug_parse(num, val, ret[4])
            if num == token.STRING:
                if not val.strip().startswith('r'):
                    # "\N{...}" is a special operator in unicode string
                    val = re.sub(r'\\+N([^{])', r'_N\g<1>', val)
            if num == token.NEWLINE:
                eoi.append(ret[2][0])
            buff.append((num, val))
            if num in (token.NEWLINE, token.ENDMARKER):
                buff = _replace_variable(buff)
                started = False
            elif num == tokenize.COMMENT and len(buff) == 1:
                # ignore inline comment
                buff = _replace_comment(buff)
                started = False
            elif num == token.NAME and len(buff) == 1 and val == "INCLUDE":
                # silently ignore INCLUDE command and arguments
                while num not in (token.NEWLINE, token.ENDMARKER):
                    ret = next(generator)
                    num = ret[0]
                buff = []
                started = False
            if not started:
                result.extend(buff)
                # _debug_parse(tokenize.COMMENT, ">>> new buffer >>>", "???")
                buff = []
    except tokenize.TokenError as tokerr:
        last = eoi[-1] if eoi else 0
        raise ConversionError(
            tokerr, str(tokerr.args[0]), last,
            translate("AsterStudy",
                      "Uncompleted docstring or expression "
                      "starting *after* line {0} and not yet "
                      "completed at line {1}"
                      .format(last, tokerr.args[1][0]))) from tokerr
    except SyntaxError:
        # return unchanged
        return eoi, text
    changed = tokenize.untokenize(result)
    debug_message("Pre-processed text:\n", changed)
    return eoi, changed


MARK_INCLUDE = "# MissingInclude: {0}"

def comment_include(text):
    """Comment the first INCLUDE command and extract value of UNITE.

    Arguments:
        text (str): Input text of the command file.

    Returns:
        str: Same text without the first unsupported command.
    """
    inc = re.compile(r"^(?P<include> *INCLUDE *\("
                     r".*?("
                     r"UNITE *= *(?P<unit>[0-9]+)"
                     r"|DONNEE *= *[\'\"]+(?P<data>[^,\)]+)[\'\"]+"
                     r").*?\)) *;?",
                     re.M | re.DOTALL)
    mat = inc.search(text)
    if mat:
        if mat.group('unit'):
            tag = "unit:{unit}".format(**mat.groupdict())
        else:
            tag = "data:{data}".format(**mat.groupdict())
        text = inc.sub(MARK_INCLUDE.format(tag), text, count=1)
    return text

def remove_include(text):
    """Remove the commented INCLUDE command.

    Arguments:
        text (str): Input text of the command file.

    Returns:
        tuple: The first element is the text without the commented command.
        The second element is the value of UNITE or DONNEE keyword, *None* if it
        isn't found.
    """
    reinc = re.compile(MARK_INCLUDE.format('(?P<tag>.+) *$'), re.M)
    mat = reinc.search(text)
    tag = None
    if mat:
        text = reinc.sub("", text)
        tag = mat.group('tag')
    return text, tag

def include_keyword(tag):
    """Return the argument to be passed to INCLUDE from a tag as returned by
    `:py:func:comment_include`.
    """
    typ, arg = tag.split(':')
    keyword = {'unit': 'UNITE', 'data': 'DONNEE'}[typ]
    value = {'unit': int(arg), 'data': repr(arg)}[typ]
    return "{0}={1}".format(keyword, value)


def change_text(text, strict, report):
    """Check for unsupported features and change text."""
    replace = strict & ConversionLevel.Partial != 0
    for expr, msg in [
            (r"^ *(?P<name>assert|print|del)\b",
             translate("AsterStudy",
                       "'{name}' statements are ignored during import.")),
        ]:
        _expr = re.compile(expr, re.M)
        for mat in _expr.finditer(text, re.M):
            report.warn(msg.format(**mat.groupdict()))

    for expr, exc, msg in [
            (r"^ *(if|for|import|from|try|def)\b",
             "NotImplementedError",
             translate("AsterStudy",
                       "Python statements can not be edited in graphical mode."
                       "\nYou can only edit this commands file in text mode.")),
            (r"^(.*?\[ *None *\])",
             "NotImplementedError",
             translate("AsterStudy",
                       "List of code_aster results is not supported.")),
            (r"^ *[^#]*DEFI_FICHIER",
             "NotImplementedError",
             translate("AsterStudy",
                       "Command DEFI_FICHIER is not supported in "
                       "graphical mode.")),
            (r"^ *(INCLUDE)\b",
             "IncludeConversion",
             translate("AsterStudy",
                       "MissingInclude: INCLUDE needs an additional "
                       "input file")),
        ]:
        replace = replace or exc == "IncludeConversion"
        err = _check_unsupported(text, expr, exc, msg, replace)
        if err:
            text = err
            break
    return _change_text(text)


def _check_unsupported(text, expr, exctype, message, replace):
    """Check if the text contains an unsupported feature.

    In this case, it returns a text that will raise an exception,
    else it returns None.
    """
    _expr = re.compile(expr, re.M)
    mat = _expr.search(text)
    if mat:
        fmt = "raise {1}({0!r})"
        error = fmt.format(MARK + " " + message, exctype)
        if replace:
            error = _expr.sub(error + "\n" + mat.group(1), text)
        return error
    return None


def _replace_variable(buff):
    """Replacement for user variable."""
    opsep = (token.OP, ';')
    try:
        idx = buff.index(opsep)
    except ValueError:
        idx = -1
    if idx > 0 and idx != len(buff) - 1:
        return (_replace_variable(buff[:idx] + [opsep]) +
                _replace_variable(buff[idx + 1:]))

    num = [i[0] for i in buff[:3]]
    val = [i[1] for i in buff[:3]]
    if num[:2] == [token.NAME, token.OP] and val[1] == "=":
        commands = list(CATA)
        if num[2] == token.NAME and val[2] in ("CO",):
            # insert an error: raise NotImplementedError
            buff = [
                (token.NAME, "raise"),
                (token.NAME, "NotImplementedError"),
                (token.OP, "("),
                (token.STRING, '"can not assign a \'CO()\' in a Python '
                               'variable"'),
                (token.OP, ")"),
                buff[-1],
            ] + buff # pragma: no cover
        elif num[2] != token.NAME or val[2] not in commands:
            strings = []
            for i in buff[2:-1]:
                if i[1].startswith('#'):
                    break
                strings.append(i[1])
            expr = format_expr(' '.join(strings))
            buff = [
                (token.NAME, val[0]),
                (token.OP, "="),
                (token.NAME, "_CONVERT_VARIABLE"),
                (token.OP, "("),
                (token.NAME, "EXPR"),
                (token.OP, "="),
                (token.STRING, repr(expr)),
                (token.OP, ")"),
                buff[-1],
            ]
    return buff


def _replace_comment(buff):
    """Replacement for comment."""
    # remove comment mark
    text = buff[0][1]
    text = re.sub("^ *# ?", "", text)
    wrap = [
        (token.NAME, "_CONVERT_COMMENT"),
        (token.OP, "("),
        (token.NAME, "EXPR"),
        (token.OP, "="),
        (token.STRING, repr(text)),
        (token.OP, ")")
    ]
    return wrap


def is_empty_comment(comment):
    """Tells if the comment contains no text"""
    null = re.escape(r" -+=*#/_$%:,.!§\\")
    return re.search('^ *#[{0}]*$'.format(null), comment.strip()) is not None


def _debug_parse(num, val, line): # pragma: no cover
    """Debug helper"""
    if debug_mode():
        if num == token.NEWLINE:
            snum = "*" * 12
        elif num == tokenize.NL:
            snum = "+" * 12
        elif num == tokenize.COMMENT:
            snum = "#" * 12
        else:
            snum = token.tok_name[num]
        fmt = "{0:<12} {1!r:<20}: {2!r}"
        debug_message(fmt.format(snum, val, line))

def is_cmd_called(text, title):
    """
    If valid python syntax, looks for a call of a callable named 'title'.

    Returns:
        *True*: if syntactically correct and callable called
        *False*: if syntactically correct and callable not called

    Raises:
        SyntaxError: if not correct python syntax
    """
    try:
        asttree = ast.parse(text)
    except SyntaxError as err:
        errmsg = translate("AsterStudy",
                           "Syntax error when looking for the command '{0}' "
                           "in a python file.".format(title))
        raise AsterStudyError(errmsg, str(err)) from err
    for node in ast.walk(asttree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == title:
                return True
    return False

def add_debut_fin(text, start, lang=None, console=False):
    """Add DEBUT and FIN commands to text if necessary.

    Arguments:
        text (str): Input text of a commands file.
        start (bool): *True* if it starts the case.
        lang (str): Language to be used or *None*.
        console (bool): Tell if the commands will be run in a console.

    Returns:
        str: Text of the commands file enclosed by DEBUT/FIN.
    """
    text = to_unicode(text)
    first_cmd = 'DEBUT' if start else 'POURSUITE'
    args = ""
    args += "" if not lang else "LANG='{0}', ".format(lang.upper())
    args += "" if not console else "PAR_LOT='NON', "
    args = re.sub(", $", "", args)
    try:
        if not (is_cmd_called(text, first_cmd) or
                re.search(r"^code_aster\.init", text, re.M) is not None):
            text = "{cmd}({args})\n\n".format(cmd=first_cmd, args=args) + text
        if not console and not (is_cmd_called(text, 'FIN') or
                                re.search(r"^code_aster\.close", text, re.M)
                                is not None):
            text = text.rstrip() + "\n\nFIN()"
    except AsterStudyError:
        # text unchanged
        pass
    return text
