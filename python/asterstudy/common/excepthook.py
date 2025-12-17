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
Exception hook
--------------

The module implements custom exception handling mechanism.

"""


import sys

from .utilities import show_exception


__all__ = ["enable_except_hook"]


def custom_except_hook(exc_type, exc_value, exc_traceback):
    """
    Custom exception handling method.

    Arguments:
        exc_type (type): Exception type (not used).
        exc_value (Exception): Exception value.
        exc_traceback (traceback): Exception traceback.
    """
    # pragma pylint: disable=unused-argument
    show_exception(exc_value, traceback=exc_traceback)


def enable_except_hook(is_enable):
    """
    Enable/disable custom exception handling.

    Arguments:
        is_enable (bool): *True* to enable, or *False* to disable
            custom exception handling.
    """
    if is_enable:
        if not hasattr(enable_except_hook, "old_hook"):
            enable_except_hook.old_hook = sys.excepthook
        sys.excepthook = custom_except_hook
    else:
        if hasattr(enable_except_hook, "old_hook"):
            old_hook = enable_except_hook.old_hook
            delattr(enable_except_hook, "old_hook")
        else:
            old_hook = sys.__excepthook__
        sys.excepthook = old_hook
