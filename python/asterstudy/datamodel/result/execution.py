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
Execution objects
-----------------

Implementation of objects that give access to execution results.

"""

from ...common import no_new_attributes, to_list
from .utils import StateOptions


class Result:
    """Implementation of the result."""

    _state = _stage = _has_remote = _messages = None
    __setattr__ = no_new_attributes(object.__setattr__)

    def __init__(self, stage):
        """
        Create Result object.

        Arguments:
            stage (Stage): Parent Stage.
            name (Optional[str]): Name of Result. Defaults to *None*.
        """
        self._stage = stage
        self._state = StateOptions.Waiting
        self._has_remote = False
        self._messages = []

    @property
    def stage(self):
        """Stage: Attribute that holds Result's parent stage."""
        return self._stage

    @stage.setter
    def stage(self, value):
        """Set Result's parent stage."""
        self._stage = value

    @property
    def state(self):
        """int: Attribute that holds Result's status (*StateOptions*)."""
        return self._state

    @state.setter
    def state(self, value):
        """Set Result's status.

        Arguments:
            value (StateOptions): new state of the Result (an intermediate
                state stays intermediate).
        """
        if self.is_intermediate():
            self._state = value | StateOptions.Intermediate
        else:
            preceding_stages = list(self._stage.preceding_stages)
            for stg in reversed(preceding_stages):
                if not stg.is_intermediate():
                    break
                stg.state = value
            self._state = value

    def is_intermediate(self):
        """Tell if the stage is an intermediate one
        (means executed grouped with the following).
        """
        return bool(self._state & StateOptions.Intermediate)

    @property
    def folder(self):
        """Return the folder containing the result files.

        Returns:
            str: Path to results directory.
        """
        stage = self._stage
        if self.is_intermediate():
            stage = stage.parent_case.get_stage_by_num(stage.number + 1)
        return stage.folder

    @property
    def used_in_cases(self):
        """list[Case]: Attribute that holds list of Cases where this
        Result is used."""
        return self._stage.cases

    @property
    def has_remote(self):
        """bool: if result databases are kept on remote execution server."""
        return self._has_remote

    @has_remote.setter
    def has_remote(self, value):
        """To set the keep-on-remote property for result databases."""
        self._has_remote = value

    def clear(self):
        """Clear result."""
        self._state = StateOptions.Waiting

    def __str__(self):
        """Get Result's representation as string."""
        return 'Result-' + self._stage.name

    def __repr__(self):
        """Get stringified representation of the result."""
        return "{0} <{1}>".format(str(self), StateOptions.name(self.state))

    def __mul__(self, other):
        """Support native Python '*' operator protocol."""
        assert self.state == other.state \
            and self._stage.name == other.stage.name

    @property
    def messages(self):
        """Get the list of messages of this execution.

        Messages are returned in the order of creation that is supposed to be
        the raising order.
        """
        return self._messages

    def clear_messages(self):
        """Clear the list of messages of this execution.

        Useful to extract messages from a new fresh output file.
        """
        self._messages = []

    def add_messages(self, msglist):
        """Add messages to the list of messages of this execution.

        Arguments:
            msglist (list[Message]): List of messages to be added.
        """
        existing = [msg.checksum for msg in self._messages]
        for msg in to_list(msglist):
            if msg.checksum not in existing:
                msg.set_stage(self.stage)
                self._messages.append(msg)
