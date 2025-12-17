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

# person_in_charge: mathieu.courtois@edf.fr

from functools import wraps

from .SyntaxUtils import mixedcopy, remove_none


def work_on_copy(func):
    """Decorator to automatically copy the keywords dict argument and remove
    None (that means undefined) values before calling a function."""

    @wraps(func)
    def wrapper(self, dict_orig):
        """wrapper"""
        dict_arg = mixedcopy(dict_orig)
        remove_none(dict_arg)
        return func(self, dict_arg)

    return wrapper


class Rule:
    """Abstract class for rules.

    Arguments:
        *args: list of keywords.
    """

    def __init__(self, *args):
        """Initialization"""
        self.ruleArgs = args

    def __repr__(self):
        """Simple representation"""
        return "%s( %r )" % (self.__class__, self.ruleArgs)

    def check(self, dictSyntax):
        """Check the rule"""
        if not isinstance(dictSyntax, dict):
            raise TypeError("'dict' is expected")

    def _firstExists(self, dictSyntax):
        """Filter that tells if the first keyword exists"""
        return self.ruleArgs[0] in dictSyntax

    def _nbValues(self, dictSyntax):
        """Returns the number of defined (not None) values"""
        return sum([i in dictSyntax for i in self.ruleArgs if dictSyntax.get(i) is not None])


class RuleWithDefaults(Rule):
    """Abstract class for rules with default values.

    Arguments:
        *args: list of keywords.
        **kwargs: default values.
    """

    def __init__(self, *args, **kwargs):
        """Initialization"""
        self.ruleArgs = args
        unknown = [key for key in kwargs if key not in args]
        if unknown:
            raise ValueError("Default values must be in arguments, not exist: {}".format(unknown))
        self.ruleKwargs = kwargs


class AtLeastOne(RuleWithDefaults):
    """Check that at least one keyword from a list is defined.

    If no keyword from the list exist, default values may be inserted if provided in ``kwargs``.
    """

    def check(self, dictSyntax):
        """Check the rule"""
        super().check(dictSyntax)
        if self._nbValues(dictSyntax) < 1:
            if self.ruleKwargs:
                dictSyntax.update(self.ruleKwargs)
            else:
                raise ValueError(
                    "At least one argument of {} must be defined".format(self.ruleArgs)
                )


class ExactlyOne(RuleWithDefaults):
    """Check that exactly one keyword from a list is defined.

    If no keyword from the list exist, a default value may be inserted if provided in ``kwargs``.
    """

    def check(self, dictSyntax):
        """Check the rule"""
        super().check(dictSyntax)
        if self._nbValues(dictSyntax) == 0 and self.ruleKwargs:
            dictSyntax.update(self.ruleKwargs)
        if self._nbValues(dictSyntax) != 1:
            raise ValueError("Exactly one argument of {} is required".format(self.ruleArgs))


class AtMostOne(Rule):
    """Check that at most one keyword from a list is defined."""

    @work_on_copy
    def check(self, dictSyntax):
        """Check the rule"""
        super().check(dictSyntax)
        if self._nbValues(dictSyntax) > 1:
            raise ValueError("At most one argument of {} can be defined".format(self.ruleArgs))


class IfFirstAllPresent(Rule):
    """Check that if a keyword is defined all others from the list
    are defined."""

    @work_on_copy
    def check(self, dictSyntax):
        """Check the rule"""
        super().check(dictSyntax)
        if self._firstExists(dictSyntax) and self._nbValues(dictSyntax) != len(self.ruleArgs):
            raise ValueError("{} must be all defined".format(self.ruleArgs[1:]))


class OnlyFirstPresent(Rule):
    """Check that if a keyword is defined no of the others from the list
    is defined."""

    @work_on_copy
    def check(self, dictSyntax):
        """Check the rule"""
        super().check(dictSyntax)
        if self._firstExists(dictSyntax) and self._nbValues(dictSyntax) != 1:
            raise ValueError("{} must be all undefined".format(self.ruleArgs[1:]))


class AllTogether(Rule):
    """Check that if all the keywords from the list are defined or
    all undefined."""

    @work_on_copy
    def check(self, dictSyntax):
        """Check the rule"""
        super().check(dictSyntax)
        if self._nbValues(dictSyntax) not in (0, len(self.ruleArgs)):
            raise ValueError("{} must be all defined or all undefined".format(self.ruleArgs))


class NotEmpty(Rule):
    """Check that at least one keyword is provided."""

    @work_on_copy
    def check(self, dictSyntax):
        """Check the rule"""
        super().check(dictSyntax)
        if not dictSyntax:
            raise ValueError("At least one argument must be defined")
