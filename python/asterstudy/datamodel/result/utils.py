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
Utilities for results
---------------------

Generic objects used for the results.

"""


import logging
from collections import OrderedDict

from ...common import translate


class RunOptions:
    """
    Enumerator for run options.

    Attributes:
        Skip: Skip stage.
        Reuse: Reuse stage.
        Execute: Execute stage.
    """
    Skip = 0x00
    Reuse = 0x01
    Execute = 0x02


class StateOptions:
    """
    Enumerator for result status.

    Attributes:
        Waiting: Execution is not started.
        Pending: Execution submitted and not running.
        Running: Execution is running.
        Pausing: Execution is suspended.
        Success: Execution was finished successfully.
        Error: Execution was failed.
        Interrupted: Execution was interrupted by an error, but partial results
            are available.
        Intermediate: No execution, the stage will be run with the following
            one and it will not be reusable.

        Warn: Execution emitted a warning.
        Nook: Invalid testcase execution (nook or no test).
        CpuLimit: Execution ended with cpu time error.
        NoConvergence: Execution ended with no convergence error.
        Memory: Execution ended with a memory error.

        Finished: Execution is finished (or not necessary for Intermediate).
        NotFinished: Execution is not finished.
    """
    # not ended states (first bit)
    Waiting = 0x001
    Pending = 0x002
    Running = 0x004
    Pausing = 0x008
    # ended states (second bit)
    Success = 0x010
    Error = 0x020
    Interrupted = 0x040
    Intermediate = 0x080
    # additionnal diagnostic (3rd and 4th bits)
    Warn = 0x0100
    Nook = 0x0200
    CpuLimit = 0x0400
    NoConvergence = 0x0800
    Memory = 0x1000
    # global
    Finished = Success | Error | Interrupted | Intermediate
    NotFinished = Waiting | Pending | Running | Pausing

    @staticmethod
    def name(state):
        """
        Convert result status to string representation (for primary states
        only).

        Arguments:
            state (int): Result status (*StateOptions*).

        Returns:
            str: String representation of status.
        """
        strings = OrderedDict([
            (StateOptions.Waiting, "Waiting"),
            (StateOptions.Pending, "Pending"),
            (StateOptions.Running, "Running"),
            (StateOptions.Pausing, "Pausing"),
            (StateOptions.Success, "Success"),
            (StateOptions.Error, "Error"),
            (StateOptions.Interrupted, "Interrupted"),
            (StateOptions.Warn, "Warn"),
            (StateOptions.Nook, "Nook"),
            (StateOptions.CpuLimit, "CpuLimit"),
            (StateOptions.NoConvergence, "NoConvergence"),
            (StateOptions.Memory, "Memory"),
            (StateOptions.Intermediate, "Intermediate"),
        ])
        sname = []
        for state_value, state_string in strings.items():
            if state & state_value:
                sname.append(state_string)
        return "Unknown" if not sname else "+".join(sname)

    @staticmethod
    def from_exit(value):
        """Convert an exit code in a state."""
        if value == 0:
            return StateOptions.Success
        return StateOptions.Error


class MsgLevel:
    """Enumerator for message level.

    Attributes:
        Debug: debugging message.
        Info: information message.
        Warn: warning message.
        Error: error message.
    """
    Debug = logging.DEBUG
    Info = logging.INFO
    Warn = logging.WARN
    Error = logging.ERROR

    @staticmethod
    def to_str(level):
        """Convert message level to string representation.

        Arguments:
            level (int): Message level (*MsgLevel*).

        Returns:
            str: String representation of the level.
        """
        return {
            MsgLevel.Debug: translate("Message", "DEBUG"),
            MsgLevel.Info: translate("Message", "INFO"),
            MsgLevel.Warn: translate("Message", "WARNING"),
            MsgLevel.Error: translate("Message", "ERROR"),
        }[level]


class MsgType:
    """Enumerator for message type.

    Attributes:
        Runner: means that the message is emitted by the runner before of after
            the code_aster execution. The identifier is 0 before starting
            code_aster, 1 after the first execution, 2 after the second and
            so on.

        Stage: means that the message is emitted during the execution of a text
            stage. The identifier is the stage number and the number of the
            related line or 0 if it is not known.

        Command: means that the message is emitted by a command. The identifier
            is the command identifier in the DataModel.
    """
    Runner = 0
    Stage = 1
    Command = 2

    @staticmethod
    def to_str(typ):
        """Convert message type to string representation.

        Arguments:
            typ (int): Message type (*MsgType*).

        Returns:
            str: String representation of the type.
        """
        return {
            MsgType.Runner: translate("Message", "Runner"),
            MsgType.Stage: translate("Message", "Stage"),
            MsgType.Command: translate("Message", "Command"),
        }[typ]
