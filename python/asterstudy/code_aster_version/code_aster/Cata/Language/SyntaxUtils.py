# coding=utf-8
# --------------------------------------------------------------------
# Copyright (C) 1991 - 2023 - EDF R&D - www.code-aster.org
# This file is part of code_aster.
#
# code_aster is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# code_aster is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with code_aster.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------

"""
List of utilities for syntax objects.
"""

import inspect
import math
import os
import sys
import warnings
from array import array
from collections import OrderedDict
from functools import partial
from warnings import showwarning, warn

import numpy

from .DataStructure import AsType


def warn_to_stdout(message, category, filename, lineno, file=None, line=None):
    """Same as `showwarning` but on stdout"""
    return showwarning(message, category, filename, lineno, file=sys.stdout, line=line)


warnings.showwarning = warn_to_stdout


def deprecate(feature, case=1, help=None, level=6):
    """Deprecate a feature, emit a deprecation warning depending on the case.

    Arguments:
        feature (str): Deprecated feature.
        case (int):
            Case 1: the feature still works but it will be removed.
            Case 2: the feature does nothing, it has been removed.
            Case 3: the feature still works but has a new implementation.
            Case 4: the feature does nothing but has a new implementation.
        help (str): Additional help message, should be present for case 3.
        level (int): Level of the caller in the stack.
    """
    if case == 1:
        msg = "This feature is obsoleted, {0!r} will be removed in the future."
    elif case == 2:
        msg = "This feature is obsoleted, {0!r} has been removed."
    elif case == 3:
        msg = "This feature has a new implementation, {0!r} will be removed in the future."
    elif case == 4:
        msg = "This feature has a new implementation, {0!r} has been removed."
    else:
        msg = "This feature is obsoleted: {0!r}"
    if help:
        msg += " " + help
    warn(msg.format(feature), DeprecationWarning, stacklevel=level)


def mixedcopy(obj):
    """Make a mixed copy (copy of all dicts, lists and tuples, no copy
    for all others)."""
    if isinstance(obj, list):
        new = [mixedcopy(i) for i in obj]
    elif isinstance(obj, tuple):
        new = tuple(mixedcopy(list(obj)))
    elif isinstance(obj, dict):
        new = obj.__class__([(i, mixedcopy(obj[i])) for i in obj])
    else:
        if hasattr(obj, "evaluation"):
            obj = obj.evaluation
        new = obj
    return new


def is_undefined(value):
    """Return *True* if the value is a null value (undefined keyword),
    *False* otherwise."""
    return value is None or (
        isinstance(value, (list, tuple))
        and (len(value) == 0 or (len(value) == 1 and value[0] is None))
    )


def remove_none(obj):
    """Remove undefined values from dict **in place**, do not change other values.
    Undefined values are *None*, empty list or empty tuple (consistent with
    `:py:func:PartOfSyntax.undefined`).

    Arguments:
        obj (list|tuple|dict): Set of user's keywords.
    """
    if isinstance(obj, (list, tuple)):
        for i in obj:
            remove_none(i)
    elif isinstance(obj, dict):
        for key, value in list(obj.items()):
            if is_undefined(value):
                del obj[key]
            else:
                remove_none(obj[key])


def add_none_sdprod(sd_prod, dictargs):
    """Check if some arguments are missing to call *sd_prod* function and
    add them with the *None* value.

    It could be considered as a catalog error. *sd_prod* function should
    not take optional keywords as arguments.

    Arguments:
        sd_prod (callable): *sd_prod* function to inspect.
        dictargs (dict): Dict of keywords, changed in place.
    """
    sign = inspect.signature(sd_prod)
    required = []
    for param in sign.parameters.values():
        if param.default is not param.empty:
            break
        required.append(param.name)

    args = list(dictargs.keys())
    # add 'self' for macro
    required.append("self")
    miss = set(required).difference(args)
    if len(miss) > 0:
        # miss = sorted(list(miss))
        # raise ValueError("Arguments required by the function:\n    {0}\n"
        #                  "Provided in dict:    {1}\n"
        #                  "Missing:    {2}\n"\
        #                  .format(sorted(required), sorted(args), miss))
        for i in miss:
            dictargs[i] = None


def search_for(obj, predicate):
    """Return all values that verify the predicate function."""
    found = []
    if isinstance(obj, (list, tuple)):
        for i in obj:
            found.extend(search_for(i, predicate))
    elif isinstance(obj, dict):
        for key, value in list(obj.items()):
            if predicate(value):
                found.append(value)
            else:
                found.extend(search_for(obj[key], predicate))
    return found


def force_list(values):
    """Ensure `values` is iterable (list, tuple, array...) and return it as
    a list."""
    if not value_is_sequence(values):
        values = [values]
    return list(values)


def value_is_sequence(value):
    """Tell if *value* is a valid object if max > 1."""
    return type(value) in (list, tuple, array, numpy.ndarray)


def array_to_list(obj):
    """Convert an object to a list if possible (using `tolist()`) or keep it
    unchanged otherwise.

    Arguments:
        obj (misc): Object to convert.

    Returns:
        misc: Object unchanged or a list.
    """
    try:
        return obj.tolist()
    except AttributeError:
        return obj


# same function exist in asterstudy.datamodel.aster_parser
def old_complex(value):
    """Convert an old-style complex."""
    if isinstance(value, (list, tuple)) and len(value) == 3:
        if value[0] == "RI":
            value = complex(value[1], value[2])
        elif value[0] == "MP":
            value = complex(
                value[1] * math.cos(value[2] * math.pi / 180.0),
                value[1] * math.sin(value[2] * math.pi / 180.0),
            )
    return value


def convert_complex(value):
    """Force conversion from real to complex numbers.

    Arguments:
        value (float|complex|tuple): Real, complex, old-complex or list of
            these types.

    Returns:
        complex|list[complex]: Complex of list of complex.
    """
    value = old_complex(value)
    if isinstance(value, (int, float, complex)):
        return complex(value)
    return [old_complex(i) for i in value]


def enable_0key(values):
    """Emulate the legacy MCFACT behavior: MCFACT[0] returns MCFACT itself
    to simulate a list of length 1.

    **Note**: `disable_0key()` must be called after to restore the original
    content of `values`.

    Arguments:
        dict: Dict of keywords changed in place.
    """
    for k, kw in list(values.items()):
        if isinstance(kw, dict):
            kw[0] = kw


def disable_0key(values):
    """Restore the content of `values` after calling `enable_0key()`.

    Arguments:
        dict: Dict of keywords changed in place.
    """
    for k, kw in list(values.items()):
        if isinstance(kw, dict) and 0 in kw:
            del kw[0]


# Keep consistency with SyntaxUtils.block_utils from AsterStudy
def block_utils(evaluation_context):
    """Define some helper functions to write block conditions.

    Arguments:
        evaluation_context (dict): The context containing the keywords.
    """

    def exists(name):
        """Tell if the keyword name exists in the context.
        The context is set to the evaluation context. In the catalog, just
        use: `exists("keyword")`"""
        return evaluation_context.get(name) is not None

    def is_in(name, values):
        """Checked if the/a value of 'keyword' is at least once in 'values'.
        Similar to the rule AtLeastOne, 'keyword' may contain several
        values."""
        name = force_list(name)
        values = force_list(values)
        # convert name to keyword
        keyword = []
        for name_i in name:
            if not exists(name_i):
                return False
            value_i = force_list(evaluation_context[name_i])
            keyword.extend(value_i)
        test = set(keyword)
        values = set(values)
        return not test.isdisjoint(values)

    def value(name, default=""):
        """Return the value of a keyword or the default value if it does
        not exist.
        The *default* default value is an empty string as it is the most
        used type of keywords."""
        return evaluation_context.get(name, default)

    def is_type(name):
        """Return the type of a keyword."""
        return AsType(value(name))

    equal_to = is_in

    def size(name):
        """Get the size of argument of a given keyword"""
        return len(evaluation_context.get(name))

    def less_than(name, test_value):
        """Return True if the value of keyword is less than test_value."""
        return value(name) < test_value

    def greater_than(name, test_value):
        """Return True if the value of keyword is grower than test_value."""
        return value(name) > test_value

    return locals()


def sorted_dict(kwargs):
    """Sort a dict in the order of the items."""
    if not kwargs:
        # empty dict
        return OrderedDict()
    vk = sorted(zip(list(kwargs.values()), list(kwargs.keys())))
    newv, newk = list(zip(*vk))
    return OrderedDict(list(zip(newk, newv)))


def debug_mode():
    """
    Check if application is running in DEBUG mode.

    Returns:
        int: 0 if DEBUG mode is switched OFF; 1 or more otherwise.
    """
    debug = getattr(debug_mode, "DEBUG", 0)
    debug = debug or int(os.getenv("DEBUG", 0))
    return debug


def debug_message(*args, **kwargs):
    """
    Print debug message.

    While this function is mainly dedicated for printing textual
    message, you may pass any printable object(s) as parameter.

    Example:
        >>> from asterstudy.common.utilities import debug_message, debug_mode
        >>> previous = debug_mode()
        >>> debug_mode.DEBUG = 1
        >>> debug_message("Start operation:", "Compute", "[args]", 100)
        AsterStudy: Start operation: Compute [args] 100
        >>> debug_message("Operation finished:", "Compute")
        AsterStudy: Operation finished: Compute
        >>> debug_mode.DEBUG = previous

    Note:
        Message is only printed if application is running in debug mode.
        See `debug_mode()`.

    Arguments:
        *args: Variable length argument list.
    """
    level = kwargs.get("level", 0)
    if debug_mode() > level:
        if args:
            print("AsterStudy:" + (" " + "." * level if level else ""), end=" ")
            for arg in args:
                print(arg, end=" ")
            print()


# pragma pylint: disable=invalid-name
debug_message2 = partial(debug_message, level=1)
# avoids to document the wrapper here and in all modules that import it
debug_message2.__doc__ = None
