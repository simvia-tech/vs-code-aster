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
Define a basic template engine.

"""


import string


class BasicFormatter(string.Formatter):
    """Basic Template engine that supports loops and conditions."""

    def format_field(self, value, format_spec):
        """Override native `:func:string.format` function."""
        if format_spec.startswith('repeat'):
            template = format_spec.partition(':')[-1]
            if isinstance(value, dict):
                value = value.items()
            return ''.join([template.format(item=item) for item in value])
        if format_spec == 'call':
            return value()
        if format_spec.startswith('if'):
            return format_spec.partition(':')[-1] if value else ''
        return super().format_field(value, format_spec)
