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
Utilities
---------

Auxiliary utilities for AsterStudy application.

"""


import getpass
import math
import os
import os.path as osp
import re
import sys
import tempfile
import time
import traceback
import zipfile
from collections import OrderedDict
from contextlib import contextmanager
from functools import partial, wraps
from itertools import product


from .base_utils import to_unicode

def debug_mode(raw=False):
    """
    Check if application is running in debug mode.

    By default (*raw* is *False*), function returns 0 if DEBUG <= 0,
    that means debug mode is switched OFF (not visible), or the DEBUG
    flag's value if it's positive.
    If *raw* is *True*, function returns actual value of DEBUG flag;
    this feature is used by `debug_message()` function.

    Arguments:
        raw (Optional[bool]): If *True*, return actual value of DEBUG
            flag; else return its normalized value. Defaults to *False*.

    Returns:
        int: Value of DEBUG flag.

    See also:
        `debug_message()`
    """
    # debug_mode.DEBUG attribute is only used for unittest
    try:
        debug = getattr(debug_mode, "DEBUG")
    except AttributeError:
        try:
            debug = int(os.getenv("DEBUG"))
        except (TypeError, ValueError):
            debug = 0
    if not raw:
        debug = max(0, debug)
    return debug


def translate(context, source_text, disambiguation=None, num=-1):
    """
    Stub translation function (no Qt dependency).
    """
    return to_unicode(source_text)

def clean_text(text):
    """Supprime les espaces superflus dans le texte."""
    return re.sub(r'\s+', ' ', text).strip()

def debug_message(*args, **kwargs):
    """
    Print debug message.

    While this function is mainly dedicated for printing textual
    message, you may pass any printable object(s) as parameter.

    The behavior of function depends on the value of DEBUG flag
    (see `debug_mode()` function), as follows:

    - DEBUG = 0: no debug information;
    - DEBUG > 0: print debug informations to stdout;
    - DEBUG < 0: write debug informations to a file
      (``/tmp/asterstudy-main-"username".log``).

    Example:
        >>> from asterstudy.common.utilities import debug_message, debug_mode
        >>> previous = debug_mode()
        >>> debug_mode.DEBUG = 1
        >>> debug_message.timestamp = False
        >>> debug_message("Start operation:", "Compute", "[args]", 100)
        AsterStudy: Start operation: Compute [args] 100
        >>> debug_message("Operation finished:", "Compute")
        AsterStudy: Operation finished: Compute
        >>> debug_mode.DEBUG = previous

    Note:
        - Message is only printed if application is running in debug
          mode. See `debug_mode()`.
        - `debug_message.timestamp` only exists for doctest.

    Arguments:
        *args: Variable length argument list.
        **kwargs: Keyword arguments.

    The following named parameters can be passed via `**kwargs`:

    - *level* (int): Indentation level.
    - *mode* (int): Used to force the debug mode (use 1 to force printing).

    See also:
        `debug_mode()`
    """
    level = kwargs.get('level', 0)
    mode = kwargs.get('mode', debug_mode(raw=True))
    if mode != 0 and kwargs.get('caller'):
        args = [debug_caller(start=2, limit=kwargs.get('limit', 2)), ]
    if mode != 0 and args:
        stream = sys.stdout
        if mode < 0:
            stream = LogFiles.file(name="main")
        text = []
        stamp = "AsterStudy:"
        if getattr(debug_message, 'timestamp', True):
            stamp += " " 
        text.append(stamp + ("." * abs(level) if level else ""))
        for i in args:
            if not isinstance(i, str):
                i = str(i)
            text.append(to_unicode(i))
        line = " ".join(text)
        stream.write(line)
        stream.write("\n")
        stream.flush()


debug_message2 = partial(debug_message, level=1) # pragma pylint: disable=invalid-name
info_message = partial(debug_message, # pragma pylint: disable=invalid-name
                       mode=1 - int(os.getenv("ASTERSTUDY_WITHIN_TESTS", "0"))
                      )


def format_code(text, style='facebook', **kwargs):
    """
    Format the given Python code.

    Style name can be specified via `style` argument. Allowed styles
    are those supported by yapf package.

    It is possible to customize standard behavior by specifying options
    via the keyword arguments. For example, maximum line length can be
    changed via COLUMN_LIMIT options.

    Arguments:
        text (str): Source code block.
        style (Optional[str]): Formatting style. Defaults to 'facebook'.
        kwargs: Keyword arguments.

    Returns:
        str: Formatted code block (or original if yapf not available).
    """
    try:
        from yapf.yapflib.yapf_api import FormatCode, style as yapf_style
        if kwargs:
            customizer = yapf_style.CreateStyleFromConfig(style)
            customizer.update(kwargs)
            style = ' '.join(['{}={}'.format(i, j) for i, j in customizer.items()])
            style = style.join('{}')
        return FormatCode(text, style_config=style)[0]
    except ImportError:
        debug_message("yapf not available: code not formatted")
        return text

def show_exception(exception, **kwargs):
    return 



def change_cursor(func):
    """Decorator for long functions to be wrapped with
    `wait_cursor(True/False)`.

    Arguments:
        func (callable): Function to be wrapped.
    """
    @wraps(func)
    def wrapper(*args, **kargs):
        """wrapper"""

    return "wrapper"    


def format_expr(text):
    """ 
    Format the given Python expression.

    Arguments:
        text (str): Source code block.

    Returns:
        str: Formatted code block.
    """
    try:
        return format_code(text)[:-1]
    except SyntaxError:
        return text


def never_fails(func):
    """Decorator that ensures a function never fails."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        """Wrapper"""
        retcode = None
        try:
            retcode = func(*args, **kwargs)
        except Exception: # pragma pylint: disable=broad-except
            debug_message("never_fails:", traceback.format_exc())
        return retcode
    return wrapper


@contextmanager
def enable_autocopy(case, changed=True):
    """
    Context manager enabling automatic copy.

    When a stage is referenced both by the current case
        and an executed case, and a modification is asked
        on this stage, automatic copy is the process by which
        that stage is copied. The copy will be referenced by
        the extecuted case. The modification is performed
        on the original, and referenced by the current case only.

    Read more details in the const_correctness module.

    Arguments:
        case (Case): current case
        changed (Optional[bool]): Tells if data model can be changed
            during the operation. Defaults to *True*.
    """
    if changed and case.model:
        case.model.autocopy_enabled = True
    yield
    if changed and case.model:
        case.model.autocopy_enabled = False


def recursive_items(dictionary, rootkey=None):
    """
    Recursively loop on items of *dictionary* and its nested *dict* items.

    Each item is returned with its *key* in the dictionary and the occurrence
    number (or *None* if it's not in a list).
    Example:
    - "('k1', None), 3" for {'k1: 3.},
    - "('k1', None, 'k2', 0), 'x'" and "('k1', None, 'k2', 1), 'y'"
    for {'k1: {'k2': ['x', 'y']}}.

    Arguments:
        dictionary (dict): Input dictionary.

    Returns:
        generator object suitable for iterating.
    """
    for key, value in dictionary.items():
        if not isinstance(value, (list, tuple)):
            value = [value]
            enum = [None]
        else:
            enum = list(range(len(value)))
        for i, value_i in zip(enum, value):
            key_i = (rootkey or []) + [key, i]
            if isinstance(value_i, dict):
                for res in recursive_items(value_i, key_i):
                    yield res
            else:
                yield tuple(key_i), value_i


def recursive_setter(dictionary, path, value):
    """Assign a value in the dictionary at the given position.

    Arguments:
        dictionary (dict): Dictionary.
        path (tuple): Path as returned by `:func:recursive_items`.
        value (misc): New value.
    """
    path = list(path)
    current = dictionary
    while path:
        key = path.pop(0)
        occ = path.pop(0)
        if path:
            current = current[key]
            if occ is not None:
                current = current[occ]
        else:
            if occ is None:
                current[key] = value
            else:
                obj = current[key]
                new = list(obj)
                new[occ] = value
                current[key] = type(obj)(new)


def common_filters():
    """
    Get common file filters to be used in file browsing dialogs.

    Return:
       str: Set of common file filters.
    """
    filters = []
    def _get_mask(_typs):
        _mask = " ".join(["*.%s" % i for i in _typs])
        return " (%s)" % _mask
    filters.append(translate("AsterStudy", "Med files") + \
                       _get_mask(["med", "rmed", "mmed"]))
    filters.append(translate("AsterStudy", "Other mesh files") + \
                       _get_mask(["msh", "mgib", "unv", "msup"]))
    filters.append(translate("AsterStudy", "Text files") + \
                       _get_mask(["txt", "csv", "dat"]))

    # !!! ADD NEW FILTER HERE !!!

    filters.append(translate("AsterStudy", "All files") + \
                       " (*)")
    return filters


def to_list(*args):
    """
    Return input value(s) as a list.

    Each input argument is treated as follows:

    - Tuple or list is converted to list;
    - For dict, its keys are added to result;
    - Simple value is converted to a list with a single item;
    - *None* values are ignored.

    Note:
        Treating of complex values from arguments list is not done: i.e.
        tuple of lists will not be converted to single plain list of
        items from all lists enclosed to tuple.

    Arguments:
        *args: Variable length argument list of input values.

    Returns:
        list: List created from input value(s).
    """
    result = []
    for value in args:
        if isinstance(value, (list, tuple, dict)):
            result.extend(value)
        elif value is not None:
            result.append(value)
    return [i for i in result if i is not None]


# same function exist in SyntaxUtils
def old_complex(value):
    """Convert an old-style complex."""
    if isinstance(value, (list, tuple)) and len(value) == 3:
        if value[0] == 'RI':
            value = complex(value[1], value[2])
        elif value[0] == 'MP':
            value = complex(value[1] * math.cos(value[2] * math.pi / 180.),
                            value[1] * math.sin(value[2] * math.pi / 180.))
    return value


def to_type(txt, typ, default=None):
    """
    Convert text to specific type.

    Example:
        >>> from asterstudy.common.utilities import to_type
        >>> to_type("1", float)
        1.0
        >>> to_type("1e", float) is None
        True
        >>> to_type("1e", float, 100)
        100
        >>> to_type("'1.+2j'", complex)
        (1+2j)

    Arguments:
        txt (str): Text to convert.
        typ (type): Expected result type.
        default (Optional[any]): Default value to be returned if
            conversion fails. Defaults to *None*.

    Returns:
        typ: Result of conversion (*default* if conversion fails).
    """
    value = default
    try:
        if typ is complex:
            txt = old_complex(eval(txt)) # pragma pylint: disable=eval-used
        value = typ(txt)
    except Exception: # pragma pylint: disable=broad-except
        pass
    return value


class CachedValues:
    """Stores some (key, value) pairs in a cache."""

    def __init__(self, size=5):
        self._size = size
        self.clear()

    def get(self, key, default=None):
        """Return a cached value or *default*."""
        return self._cache.get(key, default)

    def discard(self, key):
        """Forget the value for *key*."""
        try:
            self._cache.pop(key)
        except KeyError:
            pass

    def set(self, key, value):
        """Store a value in the cache."""
        self.discard(key)
        # limit size of cache
        if len(self._cache) > self._size:
            self._cache.popitem(last=False)
        self._cache[key] = value

    def clear(self):
        """Empty the cache."""
        self._cache = OrderedDict()


class LogFiles:
    """Helper class to deal with global log files.

    Attributes:
        cache (dict): Dict of file objects.
    """
    cache = {}
    _user = getpass.getuser()

    @classmethod
    def file(cls, name="main", nocache=False):
        """Returns the log file to use."""
        if not nocache and cls.cache.get(name) is not None:
            return cls.cache[name]
        logfile = osp.join(tempfile.gettempdir(),
                           'asterstudy-{0}-{1}.log'.format(name, cls._user))
        if osp.isfile(logfile) and not os.access(logfile, os.W_OK):
            prefix = 'asterstudy-{0}-'.format(name)
            logfile = str(tempfile.mkstemp(prefix=prefix, suffix='.log')[1])
        # force reset
        fileobj = open(logfile, 'w')
        cls.cache[name] = fileobj
        return fileobj

    @classmethod
    def filename(cls, name="main", nocache=False):
        """Returns the name of a log file to use."""
        fileobj = cls.file(name, nocache)
        return fileobj.name


def debug_caller(start=1, limit=1):
    """Debugging utility to get the call stack."""
    stack = traceback.extract_stack(limit=limit + 2)[:-start]
    return (" < ".join(["{2}@{0}:{1}".format(osp.basename(filename), line, func)
                        for filename, line, func, _ in reversed(stack)])
           )


@contextmanager
def keepdir():
    """Context manager that preserves current working directory."""
    current_dir = os.getcwd()
    try:
        yield
    except:
        os.chdir(current_dir)
        raise
    os.chdir(current_dir)


def pack(file_name, *args, **kwargs):
    """
    Zip files and directories.

    The following keyword arguments are supported:

    - **ignore_missing** (bool): Don't raise exception if source file
      or directory is missing; defaults to *False*.

    Arguments:
        file_name (str): A path to output archive.
        *args: Files and directories to pack.
        **kwargs: Keyword arguments.

    Raises:
        AttributeError: If there's nothing to pack or if any specified
            source file or directory is missing (and *ignore_missing*
            keyword argument is not *True*).
        IOError: If output archive file could not be opened for writing.
    """
    def _zip_dir(_path, _ziph):
        for _root, _, _files in os.walk(_path):
            for _file in _files:
                _ziph.write(osp.join(_root, _file))

    if not args:
        raise AttributeError("Nothing to pack")

    zipf = None
    for name in args:
        if not osp.exists(name):
            if kwargs.get('ignore_missing', False):
                continue
            raise AttributeError("Inexistent path: '{}'".format(name))
        if zipf is None:
            zipf = zipfile.ZipFile(file_name, 'w', zipfile.ZIP_DEFLATED)
        with keepdir():
            os.chdir(osp.dirname(name))
            if osp.isdir(name):
                _zip_dir(osp.basename(name), zipf)
            else:
                zipf.write(osp.basename(name))
    if zipf is not None:
        zipf.close()


def check_version(version, ref_version, operation):
    """
    Compare given version with the reference one.

    Supported comparison operations:

    - "eq" : version is equal to reference one;
    - "ne" : version is not equal to reference one;
    - "lt" : version is less than reference one;
    - "le" : version is less than or equal to reference one;
    - "gt" : version is greater than reference one;
    - "ge" : version is greater than or equal to reference one.

    Arguments:
        version (str): Version to check.
        ref_version (str): Reference version.
        operation (str): Comparison operation..

    Returns:
        bool: *True* if version passes comparison; *False* otherwise.

    Raises:
        ValueError: In case of unsupported comparison operation.
    """
    ver1 = [int(i) for i in version.split('.')]
    ver2 = [int(i) for i in ref_version.split('.')]
    ver1 += (max(len(ver1), len(ver2)) - len(ver1)) * [0]
    ver2 += (max(len(ver1), len(ver2)) - len(ver2)) * [0]
    if operation == "eq":
        return ver1 == ver2
    if operation == "ne":
        return ver1 != ver2
    if operation == "lt":
        return ver1 < ver2
    if operation == "le":
        return ver1 <= ver2
    if operation == "gt":
        return ver1 > ver2
    if operation == "ge":
        return ver1 >= ver2
    raise ValueError("Unsupported operation {}".format(operation))


def auto_datafile_naming(nodetype, node, folder):
    """Automatically assign a default filenames to unnamed files.

    Arguments:
        node (*misc*): A *Node* as defined in GUI.
        nodetype (str): Name of the `:py:class:asterstudy.gui.NodeType`.
        folder (str): Path of the history folder.
    """
    def _assign_name(folder, stage, info, unit):
        basn = stage.name
        if not info.filename:
            others = stage.other_info_search(unit)
            if others and others[0].filename:
                info.filename = others[0].filename
            else:
                info.filename = osp.join(folder, basn + "." + str(unit))

    def _assign_stage(folder, stage):
        for unit, info in stage.handle2info.items():
            _assign_name(folder, stage, info, unit)

    # warning: value2str(NodeType.Unit) = 'File'
    assert nodetype in ('Case', 'Stage', 'File'), nodetype

    if nodetype == 'File': # datafiles.objects.File
        stg = node.stage
        unit = node.unit
        _assign_name(folder, stg, stg.handle2info[unit], unit)

    elif nodetype == 'Stage':
        _assign_stage(folder, node)

    elif nodetype == 'Case':
        for stg in node.stages:
            _assign_stage(folder, stg)


def mixedcopy(obj):
    """"Make a mixed copy (copy of all dicts, lists and tuples, use variables
    values, no copy for all others)."""
    if isinstance(obj, list):
        new = [mixedcopy(i) for i in obj]
    elif isinstance(obj, tuple):
        new = tuple(mixedcopy(list(obj)))
    elif isinstance(obj, dict):
        new = obj.__class__([(i, mixedcopy(obj[i])) for i in obj])
    else:
        if hasattr(obj, 'evaluation'):
            obj = obj.evaluation
        new = obj
    return new
